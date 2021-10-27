import os

from appLogging import get_module_logger
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
from static import p_dir, slash

module_logger = get_module_logger('firebaseMessage')
client = "fNmiZCeNS4CP_ds1Q4C1uo:APA91bEAIdE5SUAmI6MTpYAkKwtX0vRjmXu2tavv3wRRxgGjIaByPRCVWm-9rYdxsK8-IrYGoRmVDVe3LqBxcxX3oghZ_k1mZ7cfBGdsGZvbnP9UqRhV7aq8SfBb8BXiFderCULhFi2x"


class FirebaseMessage(object):
    def __init__(self, message):
        self._message = message
        self._cred = None
        self.set_credentials()
        self.initialize_firebase_admin()

    def initialize_firebase_admin(self):
        module_logger.debug('initialize_firebase_admin()')
        firebase_admin.initialize_app(self._cred)
        module_logger.debug('initialize_firebase_admin() - complete')

    def set_credentials(self):
        module_logger.debug('set_credentials()')
        key_file = p_dir + slash + "firebaseKey.json"
        module_logger.debug(f'{key_file}')
        self._cred = credentials.Certificate(key_file)
        module_logger.debug('set_credentials() - complete')

    def send(self):
        module_logger.debug('send()')

        registration_tokens = [
            client
        ]

        message = messaging.MulticastMessage(
            data={'message': f'{self._message}'},
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
