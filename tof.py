import time
import threading
import VL53L0X as VL53L0X
from appLogging import get_module_logger

module_logger = get_module_logger("tof")
timer_delay = 15


class TOF(object):
    def __init__(self):
        self._running = False
        self._ranging = False
        self._range = -1
        self._sensor = VL53L0X.VL53L0X(i2c_bus=3, i2c_address=0x29)
        self._timer = None

    def get_range(self):
        if self._running:
            start_timer = True
            if not self._ranging:
                self._ranging = True
                module_logger.debug("Start ranging")
                self._sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.LONG_RANGE)
                distance = -1
                cnt = 0
                while distance < 0 and cnt < 20:
                    cnt += 1
                    distance = self._sensor.get_distance()
                    module_logger.debug("Distance %0.1f" % distance)
                    time.sleep(0.5)
                self._sensor.stop_ranging()
                module_logger.debug("Stop ranging")
                if distance < 0:
                    module_logger.debug("Distance not found.")
                    start_timer = False
                    self.restart()
                else:
                    module_logger.debug("Range: {0}mm".format(distance))
                    self._range = distance
                    self._ranging = False
            if start_timer:
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
            self._sensor.open()
            self._timer = threading.Timer(0.1, self.get_range)
            self._timer.start()

    def stop(self):
        module_logger.debug("stop()")
        self._sensor.close()
        self._running = False

    def restart(self):
        module_logger.debug("restart()")
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self.stop()
        time.sleep(10)
        self.start()

    @property
    def range(self):
        return self._range

    @property
    def running(self):
        return self._running
