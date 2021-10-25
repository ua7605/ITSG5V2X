from gps import *
import threading

from GPSlogic.GPS import GPSDaemon
from config import TomlReader
from constant.Constants import *

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

gpsd = None


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # bring it in scope
        self.gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true

    def run(self):
        while self.running:
            if self.gpsd.waiting():
                self.gpsd.next()
            gi = GPSItem(int(round(time.time() * 1000)),
                         self.gpsd.fix.latitude,
                         self.gpsd.fix.longitude,
                         self.gpsd.fix.speed
                         )
            gi_json = json.dumps(gi.__dict__)

            time.sleep(GPS_INTERVAL_MS / 1000.0)


class GPSItem:
    def __init__(self, ts=0, lat=0, lon=0, speed=0):
        self.ts = ts
        self.lat = lat
        self.lon = lon
        self.speed = speed


class ReceiveItem:
    def __init__(self, send_id=0, send_ts=0, send_lat=0, send_lon=0, send_speed=0, r_ts=0, r_lat=0, r_lon=0, r_speed=0,
                 size=0):
        self.s_id = send_id
        self.s_ts = send_ts
        self.s_lat = send_lat
        self.s_lon = send_lon
        self.s_speed = send_speed
        self.r_ts = r_ts
        self.r_lat = r_lat
        self.r_lon = r_lon
        self.r_speed = r_speed
        self.size = size


def on_message(client, userdata, message):
    print("received message = ", str(message.payload.decode("utf-8")))
    if (gpsd.fix.mode != 200):
        millis = int(round(time.time() * 1000))
        payload = str(message.payload.decode("utf-8"))
        json_data = json.loads(payload)
        ri = ReceiveItem(json_data["id"], json_data["s_ts"], json_data["s_lat"], json_data["s_lon"],
                         json_data["s_speed"], millis, gpsd.fix.latitude, gpsd.fix.longitude, gpsd.fix.speed,
                         len(payload))
        ri_json = json.dumps(ri.__dict__)
        print(ri_json)

    else:
        print("NOFIX")


if __name__ == '__main__':

    configuration_toml_file = TomlReader.configuration_toml("config.toml")
    gpsDaemon: GPSDaemon = GPSDaemon.load_from_config(configuration=configuration_toml_file, transmitter=False)

    if len(sys.argv) != 2:
        print("Wrong number of arguments")
        exit(0)

    if (sys.argv[1] == "ITSG5"):
        # To receive message you need to listen to the port 4401 it can be found in the obu.conf
        print("IP_ADDRESS: ", IP_ADDRESS, "RX_PORT_ITSG5: ", 4401)
        sock.bind((IP_ADDRESS, 4401))
        #sock.connect((IP_ADDRESS, 4401))
        print("ITSG5 Mode, sock.bind successfully!!!")

    else:
        sock.bind((IP_ADDRESS, RX_PORT_CV2X))
        print("Usage: v2x_transmitter [ITSG5 | CV2X | MQTT]")
        exit(0)

    gpsp = GpsPoller()

    try:
        gpsp.start()

        while True:
            print("Waiting for incoming UDP message")
            data, addr = sock.recvfrom(1300)
            print("Received message: ", data)

            if gpsDaemon.get_mode() != 200:  # mode = 1 means no fix
                millis = int(round(time.time() * 1000))

                if sys.argv[1] == "ITSG5":
                    tmp = data[BTP_HEADER_SIZE:]
                    json_data = json.loads(tmp)

                elif sys.argv[1] == "CV2X":
                    json_data = json.loads(data)

                elif sys.argv[1] == "MQTT":
                    pass

                else:
                    pass
                ri = ReceiveItem(json_data["id"],
                                 json_data["s_ts"],
                                 json_data["s_lat"],
                                 json_data["s_lon"],
                                 json_data["s_speed"],
                                 millis,
                                 gpsDaemon.get_latitude(),
                                 gpsDaemon.get_longitude(),
                                 gpsDaemon.get_speed(),
                                 len(data)
                                 )
                ri_json = json.dumps(ri.__dict__)
                print(ri_json)

            else:
                print("NOFIX")

    except (KeyboardInterrupt, SystemExit):
        print("interrupted!")

    finally:
        print("Killing GPS Thread...")
        gpsp.running = False
        gpsp.join()
        print(sys.stderr, "Closing socket")
        sock.close()
