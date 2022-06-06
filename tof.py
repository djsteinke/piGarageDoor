import busio
import board
import adafruit_vl53l0x
import threading
from appLogging import get_module_logger


i2c = busio.I2C(board.D15, board.D13)
module_logger = get_module_logger("tof")
timer_delay = 15


class TOF(object):
    def __init__(self):
        self._running = False
        self._ranging = False
        self._range = -1
        self._sensor = None
        self._timer = None

    def get_range(self):
        if self._running:
            restart = False
            try:
                distance = self._sensor.range
                module_logger.debug("Range: {0}mm".format(distance))
                self._range = distance
            except RuntimeError as e:
                module_logger.error(str(e))
                restart = True

            if restart:
                self.restart()
            else:
                self._timer = threading.Timer(timer_delay, self.get_range)
                self._timer.start()

    def get_status(self):
        if self._running:
            return "running"
        else:
            return "stopped"

    def start(self):
        if not self._running:
            module_logger.debug("start()")
            self._running = True
            self._sensor = adafruit_vl53l0x.VL53L0X(i2c, 0x29)
            self._timer = threading.Timer(0.1, self.get_range)
            self._timer.start()

    def stop(self):
        module_logger.debug("stop()")
        self._running = False

    def restart(self):
        module_logger.debug("restart()")
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self.stop()
        self.start()

    @property
    def range(self):
        return self._range

    @property
    def running(self):
        return self._running
