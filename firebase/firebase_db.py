from firebase_admin import db
import threading
from appLogging import get_module_logger

module_logger = get_module_logger("firebase_db")
appKey = "garageDoor"
db_trigger = db.reference(appKey + "/trigger")


class FirebaseDB(object):
    def __init__(self):
        self._ref = db.reference(appKey)
        self._trigger = self._ref.child('trigger')

    def start(self):
        self._trigger.listen(self.listener)
        threading.Timer(5, self.trigger).start()

    def trigger(self):
        module_logger.debug('trigger...')
        self._trigger.set(True)
        threading.Timer(5, self.trigger).start()

    def listener(self, event):
        module_logger.debug('firebase listener...')
        if event.data:
            module_logger.debug('open garage door')
            self._trigger.set(False)
