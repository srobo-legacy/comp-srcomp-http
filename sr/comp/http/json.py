from enum import Enum

from flask import g
import flask.json

from sr.comp.match_period import Match
from sr.comp.http.query_utils import match_json_info


class JsonEncoder(flask.json.JSONEncoder):
    """A JSON encoder that deals with various types used in SRComp."""
    def __init__(self, *args, **kwargs):
        # The following is required because the default JSON encoder does
        # stuff with these types. We can put them back in manually ourselves
        # with the 'default' method if we require. It's a bit hacky, but it
        # works.
        # In an ideal world, the types we deal with in 'default' would have
        # approriate '_asdict' methods.
        kwargs.pop('namedtuple_as_object')
        kwargs.pop('tuple_as_array')
        super(JsonEncoder, self).__init__(*args,
                                          namedtuple_as_object=False,
                                          tuple_as_array=False,
                                          **kwargs)

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, Match):
            comp = g.comp_man.get_comp()
            return match_json_info(comp, obj)
        else:
            return super(JsonEncoder, self).default(obj)
