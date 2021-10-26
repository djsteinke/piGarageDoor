import os

from appLogging import get_module_logger
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials

module_logger = get_module_logger('firebaseMessage')


class FirebaseMessage(object):
    def __init__(self, message):
        self._message = message

    def send(self):
        client = "fNmiZCeNS4CP_ds1Q4C1uo:APA91bEAIdE5SUAmI6MTpYAkKwtX0vRjmXu2tavv3wRRxgGjIaByPRCVWm-9rYdxsK8-IrYGoRmVDVe3LqBxcxX3oghZ_k1mZ7cfBGdsGZvbnP9UqRhV7aq8SfBb8BXiFderCULhFi2x"
        key_file = os.getcwd() + "\\firebase\\firebaseKey.json"
        cred = credentials.Certificate(key_file)
        firebase_admin.initialize_app(cred)

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
            print('List of tokens that caused failures: {0}'.format(failed_tokens))
        # Response is a message ID string.
        module_logger.debug("Successfully sent message")
        print('Successfully sent message:', response)
