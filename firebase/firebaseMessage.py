from appLogging import get_module_logger
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin.exceptions import FirebaseError
from static import p_dir, slash
from relay import Relay

module_logger = get_module_logger('firebaseMessage')
client = "fNmiZCeNS4CP_ds1Q4C1uo:APA91bEAIdE5SUAmI6MTpYAkKwtX0vRjmXu2tavv3wRRxgGjIaByPRCVWm-9rYdxsK8-IrYGoRmVDVe3LqBxcxX3oghZ_k1mZ7cfBGdsGZvbnP9UqRhV7aq8SfBb8BXiFderCULhFi2x"

databaseURL = "https://rn5notifications-default-rtdb.firebaseio.com/"
appKey = "garageDoor"

key_file = p_dir + slash + "firebaseKey.json"
module_logger.debug(f'{key_file}')
cred = credentials.Certificate(key_file)

firebase_admin.initialize_app(cred, {
    'databaseURL': databaseURL
})
ref = db.reference(appKey)
db_trigger = ref.child('trigger')
db_state = ref.child('state')
state = "closed"


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
    module_logger.debug('firebase listener...')
    if event.data:
        module_logger.debug('open garage door')
        db_trigger.set(False)
        # need pin... how to handle "in progress" ???
        # relay = Relay(int(pin), complete)
        # relay.on()


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


def start_listener():
    try:
        db_trigger.listen(listener)
    except FirebaseError:
        module_logger('failed to start listener... trying again.')
        start_listener()


start_listener()
