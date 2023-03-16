from appLogging import get_module_logger
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin.exceptions import FirebaseError
from static import p_dir, slash
import threading
from relay import Relay
from urllib import request, error
from time import sleep, time
from datetime import datetime

module_logger = get_module_logger('firebaseMessage')
# pixel 3 - client = "fNmiZCeNS4CP_ds1Q4C1uo:APA91bEAIdE5SUAmI6MTpYAkKwtX0vRjmXu2tavv3wRRxgGjIaByPRCVWm-9rYdxsK8-IrYGoRmVDVe3LqBxcxX3oghZ_k1mZ7cfBGdsGZvbnP9UqRhV7aq8SfBb8BXiFderCULhFi2x"
client = "dPg56sg2Q_KVyX38XxL9TH:APA91bHJ0fm1cu20iy4lS-fZcE_MPBwkxmEGtLc_Zq2-InMVaJ_N_VB6NqTW3iffSSl_i0s2g-XYBEK8ze3arvYM8Y3aSjh7OBkVJAD5CW4UPKerXJo_v1k-7H4DvmBGE6dLW_CRwv6v"
databaseURL = "https://rn5notifications-default-rtdb.firebaseio.com/"
appKey = "garageDoor"

key_file = "/home/pi/projects/firebaseKey.json"
module_logger.debug(f'{key_file}')
cred = credentials.Certificate(key_file)

firebase_admin.initialize_app(cred, {
    'databaseURL': databaseURL
})
ref = db.reference(appKey)
db_trigger = ref.child('trigger')
db_trigger_stream = None
db_state = ref.child('state')
state = "closed"

network_up = False
timer = 0
last_listener_update = -1
reset_stream = False


def internet_on():
    global network_up, reset_stream
    while True:
        try:
            request.urlopen("http://google.com")
            if not network_up:
                module_logger.debug('Network UP.')
            network_up = True
            return network_up
        except error.URLError:
            if network_up:
                module_logger.error('Network DOWN!!!')
            network_up = False
            reset_stream = True
        sleep(15)


def trigger():
    module_logger.debug('trigger...')
    db_trigger.set(True)


def set_state(range_mm):
    global state
    state_new = "closed"
    if range_mm < 400:
        state_new = "open"
    elif range_mm < 1000:
        state_new = "full"
    if state_new != state:
        db_state.set(state_new)
    state = state_new


def listener(event):
    global timer, last_listener_update
    module_logger.debug('firebase listener...')
    last_listener_update = round(time())
    if event.data:
        trigger_time = ref.child("triggerTime").get()
        if datetime.now().timestamp() - trigger_time < 60:
            module_logger.debug('open garage door')
            # pin = 12
            relay = Relay(12, None)
            relay.on()
        else:
            module_logger.debug('garage door triggered more than 1 min ago', trigger_time)
        db_trigger.set(False)


def send(message):
    module_logger.debug('send()')

    registration_tokens = [
        client
    ]

    message = messaging.MulticastMessage(
        data={'message': f'{message}'},
        tokens=registration_tokens
    )
    response = messaging.send_multicast(message)

    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # The order of responses corresponds to the order of the registration tokens.
                failed_tokens.append(registration_tokens[idx])
        module_logger.debug('List of tokens that caused failures: {0}'.format(failed_tokens))
    # Response is a message ID string.
    module_logger.debug("Successfully sent message")


def start_listener_old():
    try:
        db_trigger.listen(listener)
    except FirebaseError:
        module_logger.error('failed to start listener... trying again.')
        start_listener_old()


def start_listener():
    global timer, db_trigger_stream, reset_stream
    while True:
        if internet_on():
            # If it has been more than an hour since the listener was triggered (automatically every hour)
            # restart the stream
            if last_listener_update < 0 or round(time()) - last_listener_update > 3660:
                module_logger.error('listener has not triggered in more than 1 hr. restart listener.')
                reset_stream = True

            if reset_stream:
                try:
                    db_trigger_stream.close()
                    module_logger.debug('stream closed...')
                except:
                    module_logger.debug('no stream to close... ')
                    pass
                try:
                    db_trigger_stream = db_trigger.listen(listener)
                    module_logger.debug('streams open...')
                    reset_stream = False
                except FirebaseError:
                    module_logger.error('failed to start listeners... ')
                    reset_stream = True
        sleep(15)
