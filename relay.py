import threading

import RPi.GPIO as GPIO
from appLogging import get_module_logger

module_logger = get_module_logger("relay")

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Relay(object):
    def __init__(self, pin, callback):
        self._on = False
        self._pin = pin
        self._delay = 1
        self._callback = callback
        GPIO.setup(self._pin, GPIO.OUT)
        if GPIO.input(self._pin) == 0:
            self._on_state = GPIO.HIGH
            self._off_state = GPIO.LOW
        else:
            self._on_state = GPIO.LOW
            self._off_state = GPIO.HIGH
        GPIO.output(self._pin, GPIO.LOW)

    def on(self):
        self._on = True
        GPIO.output(self._pin, self._on_state)
        timer = threading.Timer(self._delay, self.off)
        timer.start()

    def off(self):
        self._on = False
        GPIO.output(self._pin, self._off_state)
        if self._callback is not None:
            self._callback()
