import os

from appLogging import get_module_logger
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials
from static import p_dir

module_logger = get_module_logger('firebaseMessage')


class FirebaseMessage(object):
    def __init__(self, message):
        self._message = message

    def send(self):
        module_logger.debug('send()')
        client = "fNmiZCeNS4CP_ds1Q4C1uo:APA91bEAIdE5SUAmI6MTpYAkKwtX0vRjmXu2tavv3wRRxgGjIaByPRCVWm-9rYdxsK8-IrYGoRmVDVe3LqBxcxX3oghZ_k1mZ7cfBGdsGZvbnP9UqRhV7aq8SfBb8BXiFderCULhFi2x"
        key_file = p_dir + "\\firebaseKey.json"
        cred = credentials.Certificate(key_file)
        firebase_admin.initialize_app(cred)

        module_logger.debug('firebase_admin.initialize_app')
        registration_tokens = [
            client
        ]

        message = messaging.MulticastMessage(
            data={'message': f'{self._message}'},
            tokens=registration_tokens
        )
        module_logger.debug('messaging.MulticastMessage')
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
