import threading
import datetime as dt

from firebase.firebaseMessage import FirebaseMessage
from appLogging import get_module_logger
check_interval = 15
module_logger = get_module_logger("notify")

schedule = {'rules': [
    {'day': 7, 'ranges': [  # 0-6 Mon-Sun, 7 weekday, 8 weekend
        {'s': 0, 'e': 16, 'i': 15},  # Start, End, Interval
        {'s': 16, 'e': 18, 'i': 120},
        {'s': 18, 'e': 0, 'i': 15}]},
    {'day': 8, 'ranges': [
        {'s': 0, 'e': 7, 'i': 15},
        {'s': 7, 'e': 18, 'i': 120},
        {'s': 18, 'e': 0, 'i': 15}]}]}


class Notify(object):
    def __init__(self, tof):
        self._tof = tof
        self._running = False
        self._open = False
        self._interval = 0

    def check(self):
        r = self._tof.range
        # Check if door is open
        if 0 < r < 300:
            self._open = True
            self._interval = self._interval + 1  # If door is open, add 1 min to interval
        else:
            self._open = False
            self._interval = 0  # If door is closed, reset timer

        if self.send_notify():
            FirebaseMessage('Garage Door Open').send()  # Send message via Firebase
            self._interval = 0                          # Reset interval

        if self._running:
            timer = threading.Timer(check_interval, self.check)
            timer.start()

    def send_notify(self):
        notify = False
        hr = dt.datetime.now().hour
        day = dt.datetime.now().weekday()
        for dow in schedule['rules']:               # DAY OF WEEK rules
            if day == dow['day'] or (dow['day'] == 7 and day < 5) or (dow['day'] == 8 and day > 4):
                for hod in dow['ranges']:           # HR OF DAY rules
                    interval = 60/check_interval*hod['i']
                    if hod['s'] <= hr < hod['e'] and self._interval >= interval:
                        notify = True               # If day match and hr is within range and interval met
        return notify

    def start(self):
        self._running = True
        timer = threading.Timer(1, self.check)
        timer.start()

    def stop(self):
        self._running = False
