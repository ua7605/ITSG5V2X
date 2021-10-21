import threading
from gps import *

from constants import Constants
from GPSlogic.GPS import GPSItem


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.gpsd = gps(mode=WATCH_ENABLE)
        self.current_value = None
        self.running = True

    def run(self) -> None:
        while self.running:
            if self.gpsd.waiting():
                self.gpsd.next()
            gi = GPSItem(int(round(time.time() * 1000)), self.gpsd.fix.latitude, self.gpsd.fix.longitude,
                         self.gpsd.fix.speed)
            time.sleep(Constants.GPS_INTERVAL_MS / 1000.0)
