class Response(object):
    def __init__(self):
        self._status_code = 0
        self._action = ""
        self._data = "{}"

    def __dict__(self):
        return dict(statusCode=self._status_code,
                    data=self._data)

    @property
    def status_code(self):
        return self._status_code

    @property
    def action(self):
        return self._action

    @property
    def data(self):
        return self._data

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @action.setter
    def action(self, value):
        self._action = value

    @data.setter
    def data(self, value):
        self._data = value
