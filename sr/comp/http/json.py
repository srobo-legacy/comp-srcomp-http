from enum import Enum

import flask.json


class JsonEncoder(flask.json.JSONEncoder):
    """A JSON encoder that deals with ``Enum``s."""
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        else:
            return super().default(obj)
