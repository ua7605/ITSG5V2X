import socket
import json
import sys
import time

from constant.Constants import *
from GPSlogic.GPSPolling import GpsPoller
from Cohdas.BTPheader import BTP

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class SendItem:
    def __init__(self, id=0, ts=0, lat=0, lon=0, speed=0):
        self.id = id
        self.s_ts = ts
        self.s_lat = lat
        self.s_lon = lon
        self.s_speed = speed


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print(len(sys.argv))
        print("Wrong number of arguments")
        exit(0)

    if (sys.argv[1] == "ITSG5"):
        print("ITSG5 Mode")
        server_address = (SERVER_ADDRESS_ITSG5, TX_PORT)

    elif (sys.argv[1] == "CV2X"):
        server_address = (SERVER_ADDRESS_CV2X, TX_PORT)
        print("CV2X Mode")

    gpsp = GpsPoller()
    try:
        gpsp.start()
        i = 0

        while True:
            if (gpsp.gpsd.fix.mode != 200):  # mode = 1 means no fix
                i += 1
                millis = int(round(time.time() * 1000))
                si = SendItem(i, millis, gpsp.gpsd.fix.latitude, gpsp.gpsd.fix.longitude, gpsp.gpsd.fix.speed)

                si_json = json.dumps(si.__dict__)

                if (sys.argv[2] == "DENM"):
                    si_json = si_json.ljust(PACKET_SIZE + 1)
                else:
                    si_json = si_json.ljust(PACKET_SIZE)

                if (sys.argv[1] == "ITSG5"):
                    btp_header = BTP((len(si_json)),
                                     gpsp.gpsd.fix.latitude * 10000000,
                                     gpsp.gpsd.fix.longitude * 10000000
                                     )
                    btp_header.assemble_btp_fields()
                    sent = sock.sendto(data=btp_header.raw + si_json, address=server_address)
                    si.size = sent  # can be removed no use!

                elif (sys.argv[1] == "CV2X"):
                    sent = sock.sendto(data=si_json, address=server_address)
                    si.size = sent
                else:
                    pass

                si_json = json.dumps(si.__dict__)
                print(si_json)
            else:
                print("NOFIX")
            time.sleep(INTERVAL_MS / 1000.0)

    except (KeyboardInterrupt, SystemExit):
        print("interrupted")

    finally:
        print("Killing GPS Thread")
        gpsp.running = False
        gpsp.join()  # wait for the thread to finish what it's doing
        print(sys.stderr, "Closing socket")
        sock.close()