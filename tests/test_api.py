from __future__ import print_function

import json
import os.path
from flask.testing import FlaskClient

from sr.comp.http import app

COMPSTATE = os.path.join(os.path.dirname(__file__), 'dummy')
app.config['COMPSTATE'] = COMPSTATE

CLIENT = FlaskClient(app)

def server_get(endpoint):
    response, code, header = CLIENT.get(endpoint)
    response_code = int(code.split(' ')[0])
    response_data = b''.join(response)
    return response_code, response_data

def assert_json(endpoint, expected, expected_data=None):
    status, raw_data = server_get(endpoint)
    assert expected == status, raw_data

    data = json.loads(raw_data.decode('utf-8'))
    if expected_data is None:
        assert data is not None
    else:
        assert data == expected_data, str(data)

    return data

def test_endpoints():
    endpoints = [
        '/',
        '/arenas',
        '/arenas/A',
        '/arenas/B',
        '/teams',
        '/teams/CLF',
        '/corners',
        '/corners/0',
        '/corners/1',
        '/corners/2',
        '/corners/3',
        '/matches',
        '/matches?arenas=A&range=current',
        '/matches?arenas=B&range=current',
        '/matches?range=0-1',
        '/matches?arenas=B&range=1',
        '/matches?type=knockout',
        '/state'
    ]

    for e in endpoints:
        yield assert_json, e, 200

def test_root():
    assert_json('/', 200, {'config': '/config',
                           'arenas': '/arenas',
                           'teams': '/teams',
                           'corners': '/corners',
                           'matches': '/matches',
                           'state': '/state'})

