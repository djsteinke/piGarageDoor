import subprocess
import time

import busio
import board
import adafruit_vl53l0x
import threading
from appLogging import get_module_logger
from firebase.firebaseMessage import set_state

i2c = busio.I2C(board.SCL_2, board.SDA_2)
module_logger = get_module_logger("tof")
timer_delay = 15
restart_delay = 600


class TOF(object):
    def __init__(self, callback=None):
        self._running = False
        self._ranging = False
        self._range = -1
        self._sensor = None
        self._timer = None
        self._restart_timer = None
        self._start_callback = callback

    def get_range(self):
        if self._running:
            restart = False
            self._restart_timer = threading.Timer(restart_delay, self.restart)
            self._restart_timer.start()
            try:
                distance = self._sensor.range
                # module_logger.debug("Range: {0}mm".format(distance))
                self._range = distance
                set_state(int(distance))
            except RuntimeError as e:
                module_logger.error(str(e))
                restart = True
            self._restart_timer.cancel()
            self._restart_timer = None
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
        while not self._running:
            module_logger.debug("start()")
            try:
                self._sensor = adafruit_vl53l0x.VL53L0X(i2c, 0x29)
                module_logger.debug("_sensor")
                module_logger.debug(self._sensor)
                if self._start_callback is not None:
                    self._start_callback()
                self._running = True
                threading.Timer(0.1, self.get_range).start()
            except:
                time.sleep(1)

    def stop(self):
        module_logger.debug("stop()")
        self._running = False

    def restart(self):
        module_logger.debug("restart()")
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if self._restart_timer is not None:
            self._restart_timer = None
        stdout, stderr = subprocess.Popen(['/home/pi/projects/piGarageDoor/./mgr', 'stop'],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        module_logger.debug("stdout: " + stdout.decode())
        module_logger.error("stderr: " + stderr.decode())
        if len(stderr.decode()) > 0:
            self.stop()
            self.start()

    @property
    def range(self):
        return self._range

    @property
    def running(self):
        return self._running
