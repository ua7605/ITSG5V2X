import socket
import json
import sys
import time
import toml

from GPSlogic.GPS import GPSDaemon
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


def configuration_toml(config: str):
    try:
        with open(config) as file:
            configuration_file = toml.load(f=file)
            return configuration_file
    except:
        print("File doesn't exists: " + config)
        sys.exit(0)


if __name__ == '__main__':

    configuration_toml_file = configuration_toml("config.toml")

    if len(sys.argv) != 2:
        print(len(sys.argv))
        print(sys.argv[1])
        print("Wrong number of arguments")
        exit(0)

    if sys.argv[1] == "ITSG5":
        print("ITSG5 Mode")
        print("sending to: ", IP_ADDRESS_MK5_ITSG5, "with port number: 4401")

        server_address = (IP_ADDRESS_MK5_ITSG5, 4401)  # The port number can be found in the obu.conf file, but standard this is always 4401

    elif sys.argv[1] == "CV2X":
        # TODO: support to send also messages over CV2X
        # server_address = (SERVER_ADDRESS_CV2X, 4401)  # The port number can be found in the obu.conf file, but standard this is always 4401
        print("CV2X Mode")

    gpsp = GpsPoller()
    gpsDaemon: GPSDaemon = GPSDaemon.load_from_config(configuration=configuration_toml_file, transmitter=True)

    try:
        gpsp.start()
        i = 0

        while True:
            if gpsp.gpsd.fix.mode != 200:  # mode = 1 means no fix
                i += 1
                millis = int(round(time.time() * 1000))

                # This is the demo data that will be send over ITS-G5. But this can whatever you want.
                si = SendItem(i, millis, gpsDaemon.get_latitude(), gpsDaemon.get_longitude(), gpsDaemon.get_speed())

                si_json = json.dumps(si.__dict__)

                # If you would use DEMN you need to add one to PACKET_SIZE
                #if sys.argv[2] == "DENM":
                    #si_json = si_json.ljust(PACKET_SIZE + 1)
                #else:
                si_json = si_json.ljust(PACKET_SIZE)

                if sys.argv[1] == "ITSG5":
                    print("THis will be send: ", si_json)

                    btp_header = BTP((len(si_json)),
                                     round(gpsDaemon.get_latitude() * 10000000),
                                     round(gpsDaemon.get_longitude() * 10000000)
                                     )

                    btp_header.assemble_btp_fields()
                    print("The header is assembled !!!!")
                    to_be_send = btp_header.raw + bytes(si_json.encode('utf-8'))

                    sent = sock.sendto(to_be_send, server_address)
                    print("THe message is sent!")
                    si.size = sent  # can be removed no use!


                elif sys.argv[1] == "CV2X":
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
