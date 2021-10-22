import gpsd


class GPSItem(object):
    def __init__(self, ts=0, latitude=0, longitude=0, speed=0):
        self.ts = ts
        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed


class GPSDaemon(object):
    @staticmethod
    def load_from_config(configuration):
        gps_config = configuration["GPS"]
        gps_host_ip: str = gps_config["GPS_host_ip"]
        gps_port: int = gps_config["GPS_port"]

        return GPSDaemon(host_ip=gps_host_ip,
                         port=gps_port,
                         )

    def __init__(self, host_ip: str, port: int):
        print("Connecting to GPS....")
        gpsd.connect(host=host_ip, port=port)
        print("Connected to GPS ! ", host_ip, " port: ", port)

    def get_latitude(self):
        return gpsd.get_current().lat

    def get_longitude(self):
        return gpsd.get_current().lon
