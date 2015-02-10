from __future__ import print_function

import json
import os.path
from flask.testing import FlaskClient

from freezegun import freeze_time
from nose.tools import eq_, raises

from sr.comp.http import app

COMPSTATE = os.path.join(os.path.dirname(__file__), 'dummy')
app.config['COMPSTATE'] = COMPSTATE

CLIENT = FlaskClient(app)

class APIError(Exception):
    pass

def server_get(endpoint):
    response, code, header = CLIENT.get(endpoint)
    response_code = int(code.split(' ')[0])
    response_data = b''.join(response)
    if response_code != 200:
        raise APIError('Returned status {}'.format(response_code))
    return json.loads(response_data.decode('utf-8'))

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
        yield server_get, e

def test_root():
    eq_(server_get('/'), {'config': '/config',
                          'arenas': '/arenas',
                          'teams': '/teams',
                          'corners': '/corners',
                          'matches': '/matches',
                          'state': '/state',
                          'current': '/current'})

def test_state():
    assert isinstance(server_get('/state')['state'], str)

def test_corner():
    eq_(server_get('/corners/0'), {'get': '/corners/0',
                                   'number': 0,
                                   'colour': '#00ff00'})

@raises(APIError)
def test_invalid_corner():
    server_get('/corners/12')

def test_config():
    cfg = server_get('/config')['config']
    eq_(cfg['match_periods'], {'pre': 90,
                               'match': 180,
                               'post': 30,
                               'total': 300})

def test_arena():
    eq_(server_get('/arenas/A'), {'get': '/arenas/A',
                                  'name': 'A',
                                  'display_name': 'A'})

@raises(APIError)
def test_invalid_arena():
    server_get('/arenas/Z')

def test_arenas():
    eq_(server_get('/arenas')['arenas'],
          {'A': {'get': '/arenas/A',
                 'name': 'A',
                 'display_name': 'A'},
           'B': {'get': '/arenas/B',
                 'name': 'B',
                 'display_name': 'B'}})

def test_team():
    eq_(server_get('/teams/CLF'), {'tla': 'CLF',
                                   'name': 'Clifton High School',
                                   'scores': {'league': 68,
                                              'game': 69},
                                   'get': '/teams/CLF'})

def test_matches():
    eq_(server_get('/matches?num=0&arena=A'),
         {'matches': [
           {'num': 0,
            'arena': 'A',
            'type': 'league',
            'teams': [None, 'CLY', 'TTN', None],
            'scores': {
               'game': {'CLY': 9, 'TTN': 6},
               'league': {'CLY': 8, 'TTN': 6}
            },
            'times': {
               'period': {
                  'start': '2014-04-26T13:00:00+01:00',
                  'end':   '2014-04-26T13:05:00+01:00'
               },
               'game': {
                  'start': '2014-04-26T13:01:30+01:00',
                  'end':   '2014-04-26T13:04:30+01:00'
               }
            }}
         ]})

@freeze_time('2014-04-26 13:01:00')  # UTC
def test_current_match_time():
    eq_(server_get('/current')['time'],
        '2014-04-26T13:01:00+01:00')

@freeze_time('2014-04-26 13:01:00')  # UTC
def test_current_match():
    match_list = server_get('/current')['matches']
    match_list.sort(key=lambda match: match['arena'])
    ref = [{'num': 0,
            'arena': 'A',
            'type': 'league',
            'teams': [None, 'CLY', 'TTN', None],
            'scores': {
               'game': {'CLY': 9, 'TTN': 6},
               'league': {'CLY': 8, 'TTN': 6},
            },
            'times': {
               'period': {
                  'start': '2014-04-26T13:00:00+01:00',
                  'end':   '2014-04-26T13:05:00+01:00'
               },
               'game': {
                  'start': '2014-04-26T13:01:30+01:00',
                  'end':   '2014-04-26T13:04:30+01:00'
               }
            }},
           {'num': 0,
            'arena': 'B',
            'type': 'league',
            'teams': ['GRS', 'QMC', None, None],
            'scores': {
               'game': {'QMC': 3, 'GRS': 5},
               'league': {'QMC': 6, 'GRS': 8},
            },
            'times': {
               'period': {
                  'start': '2014-04-26T13:00:00+01:00',
                  'end':   '2014-04-26T13:05:00+01:00'
               },
               'game': {
                  'start': '2014-04-26T13:01:30+01:00',
                  'end':   '2014-04-26T13:04:30+01:00'
               }
            }}]
    eq_(match_list, ref)
