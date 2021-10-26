import threading
import datetime as dt

from firebase.firebaseMessage import FirebaseMessage
from properties import start_time, end_time
from appLogging import get_module_logger
interval = 60
module_logger = get_module_logger("notify")


class Notify(object):
    def __init__(self, tof):
        self._tof = tof
        self._running = False
        self._sent = False
        self._cnt = 0

    def check(self):
        hr = dt.datetime.now().hour
        r = self._tof.range
        module_logger.debug(f'Range[{r}]')
        # if start_time > hr >= end_time:
        if 0 < r < 300:
            if not self._sent or self._cnt > 15:
                FirebaseMessage('Garage Door Open').send()

                self._sent = True
                self._cnt = 0
            else:
                self._cnt += 1
        else:
            self._sent = False
        if self._running:
            timer = threading.Timer(interval, self.check)
            timer.start()

    def start(self):
        self._running = True
        timer = threading.Timer(0, self.check)
        timer.start()

    def stop(self):
        self._running = False
