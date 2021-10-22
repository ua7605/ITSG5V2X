import socket
import sys
import time
import json
from gps import *
import threading
from constant.Constants import *
import os
import ssl
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



global log_dir

gpsd = None


class BTP:
    def __init__(self, length, lat, lon):
        self.BTPType = ETSI_GN_NH_BTPB
        self.PktTransport = ETSI_GN_TRANSPORT_GEOBROADCAST
        self.TrafficClass = 0
        self.MaxPktLifetime = 0
        self.DestPort = BTP_PORT_DENM
        self.DestInfo = 0
        self.CommProfile = ETSI_GN_PROFILE_ITS_G5
        self.RepeatInterval = 0
        self.Length = length
        self.SecProfile = ETSI_GN_SEC_PROF_AID_SSP
        self.AID = 0x25
        self.SSPLen = 4
        self.SSPBits = [0x01, 0xFF, 0xFF, 0xFF, 0, 0]
        self.Latitude = lat
        self.Longitude = lon
        self.DistanceA = GN_GBC_DESTDISTANCEA
        self.DistanceB = GN_GBC_DESTDISTANCEB
        self.Shape = GN_GBC_DESTSHAPE
        self.Angle = GN_GBC_DESTANGLE
        self.Unused = 0

    def assemble_btp_fields(self):
        # print self.Length
        tmp = struct.pack('!BBBBHH',
                          self.BTPType,
                          self.PktTransport,
                          self.TrafficClass,
                          self.MaxPktLifetime,
                          self.DestPort,
                          self.DestInfo
                          )

        tmp += struct.pack('!IIHHHBB',
                           self.Latitude,
                           self.Longitude,
                           self.DistanceA,
                           self.DistanceB,
                           self.Angle,
                           self.Shape,
                           self.Unused
                           )

        tmp += struct.pack('!BBBBIBBBBBBH',
                           self.CommProfile,
                           self.RepeatInterval,
                           self.SecProfile,
                           self.SSPLen,
                           self.AID,
                           self.SSPBits[0],
                           self.SSPBits[1],
                           self.SSPBits[2],
                           self.SSPBits[3],
                           self.SSPBits[4],
                           self.SSPBits[5],
                           self.Length
                           )
        self.raw = tmp
        return


class GPSItem:
    def __init__(self, ts=0, lat=0, lon=0, speed=0):
        self.ts = ts
        self.lat = lat
        self.lon = lon
        self.speed = speed


def write_log(file, send_item):
    file.write(send_item + "\n")


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true
        gps_log_file = log_dir + "/tx_gps.out"
        self.gps_f = open(gps_log_file, "w+")

    def run(self):
        global gpsd
        while self.running:
            if gpsd.waiting():  # only True if data is available
                gpsd.next()
            gi = GPSItem(int(round(time.time() * 1000)), gpsd.fix.latitude, gpsd.fix.longitude, gpsd.fix.speed)
            gi_json = json.dumps(gi.__dict__)
            write_log(self.gps_f, gi_json)
            time.sleep(GPS_INTERVAL_MS / 1000.0)
        self.gps_f.close()


class SendItem:
    def __init__(self, id=0, ts=0, lat=0, lon=0, speed=0):
        self.id = id
        self.s_ts = ts
        self.s_lat = lat
        self.s_lon = lon
        self.s_speed = speed


def on_publish(client, userdata, result):  # create function for callback
    print("data published \n")
    pass


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print
        "Wrong number of arguments"
        exit(0)

    if (sys.argv[1] == "ITSG5"):
        print
        "ITSG5 Mode\n"
        #		if (sys.argv[2] == "DENM"):
        #            		server_address = (constant.SERVER_ADDRESS_ITSG5, 4404)
        #		else:
        server_address = (SERVER_ADDRESS_ITSG5, TX_PORT)

        log_dir = "./logitsg5tx/" + time.strftime("%Y%m%d%H%M%S%Z", time.localtime()) + "/"
    elif (sys.argv[1] == "CV2X"):
        server_address = (SERVER_ADDRESS_CV2X, TX_PORT)
        log_dir = "./logcv2xtx/" + time.strftime("%Y%m%d%H%M%S%Z", time.localtime()) + "/"
        print
        "CV2X Mode\n"
    else:
        print
        "Usage: v2x_transmitter [ITSG5 | CV2X | MQTT]"
        exit(0)

    print
    log_dir
    os.makedirs(os.path.dirname(log_dir))

    gpsp = GpsPoller()  # create the thread
    try:
        gpsp.start()
        i = 0
        tx_log_file = log_dir + "/tx.out"
        # filename = "./log/{}/tx.out" format(5)
        f = open(tx_log_file, "w+")

        while True:
            #			print gpsd.fix.mode
            if (gpsd.fix.mode != 200):  # mode = 1 means no fix
                i += 1
                millis = int(round(time.time() * 1000))
                si = SendItem(i, millis, gpsd.fix.latitude, gpsd.fix.longitude, gpsd.fix.speed)

                si_json = json.dumps(si.__dict__)
                if (sys.argv[2] == "DENM"):
                    si_json = si_json.ljust(PACKET_SIZE + 1)
                else:
                    si_json = si_json.ljust(PACKET_SIZE)
                if (sys.argv[1] == "ITSG5"):
                    btp_header = BTP((len(si_json)), gpsd.fix.latitude * 10000000, gpsd.fix.longitude * 10000000)
                    btp_header.assemble_btp_fields()
                    sent = sock.sendto(btp_header.raw + si_json, server_address)
                    si.size = sent
                elif (sys.argv[1] == "CV2X"):
                    sent = sock.sendto(si_json, server_address)
                    si.size = sent
                else:
                    pass
                si_json = json.dumps(si.__dict__)
                print
                si_json
                write_log(f, si_json)
            else:
                print
                "NOFIX"
            time.sleep(INTERVAL_MS / 1000.0)
    except (KeyboardInterrupt, SystemExit):
        print('interrupted!')
    finally:
        print
        "\nKilling GPS Thread..."
        gpsp.running = False
        gpsp.join()  # wait for the thread to finish what it's doing
        print >> sys.stderr, 'Closing socket'
        sock.close()
        f.close()


