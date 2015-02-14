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

class API404Error(Exception):
    pass

def server_get(endpoint):
    response, code, header = CLIENT.get(endpoint)
    response_code = int(code.split(' ')[0])
    response_data = b''.join(response)
    if response_code == 200:
        return json.loads(response_data.decode('utf-8'))
    elif response_code == 404:
        raise API404Error()
    else:
        raise APIError('Returned status {}'.format(response_code))

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
                          'current': '/current',
                          'knockout': '/knockout'})

def test_state():
    state_val = server_get('/state')['state']
    unicode = type(u'') # Python 2/3 hack
    assert isinstance(state_val, unicode), repr(state_val)

def test_corner():
    eq_(server_get('/corners/0'), {'get': '/corners/0',
                                   'number': 0,
                                   'colour': '#00ff00'})

@raises(API404Error)
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

@raises(API404Error)
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
                                   'league_pos': 13,
                                   'scores': {'league': 68,
                                              'game': 69},
                                   'get': '/teams/CLF'})

@raises(API404Error)
def test_bad_team():
    server_get('/teams/BEES')

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

@raises(APIError)
def test_invalid_match_type():
    server_get('/matches?type=bees')

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

def test_knockouts():
    import pprint
    ref = [[{'arena': 'A',
             'num': 111,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:34:30+01:00',
                                'start': '2014-04-27T15:31:30+01:00'},
                       'period': {'end': '2014-04-27T15:35:00+01:00',
                                  'start': '2014-04-27T15:30:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 111,
             'teams': ['???', '???', '???', None],
             'times': {'game': {'end': '2014-04-27T15:34:30+01:00',
                                'start': '2014-04-27T15:31:30+01:00'},
                       'period': {'end': '2014-04-27T15:35:00+01:00',
                                  'start': '2014-04-27T15:30:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 112,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:39:30+01:00',
                                'start': '2014-04-27T15:36:30+01:00'},
                       'period': {'end': '2014-04-27T15:40:00+01:00',
                                  'start': '2014-04-27T15:35:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 112,
             'teams': ['???', '???', None, '???'],
             'times': {'game': {'end': '2014-04-27T15:39:30+01:00',
                                'start': '2014-04-27T15:36:30+01:00'},
                       'period': {'end': '2014-04-27T15:40:00+01:00',
                                  'start': '2014-04-27T15:35:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 113,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:44:30+01:00',
                                'start': '2014-04-27T15:41:30+01:00'},
                       'period': {'end': '2014-04-27T15:45:00+01:00',
                                  'start': '2014-04-27T15:40:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 113,
             'teams': [None, '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:44:30+01:00',
                                'start': '2014-04-27T15:41:30+01:00'},
                       'period': {'end': '2014-04-27T15:45:00+01:00',
                                  'start': '2014-04-27T15:40:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 114,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:49:30+01:00',
                                'start': '2014-04-27T15:46:30+01:00'},
                       'period': {'end': '2014-04-27T15:50:00+01:00',
                                  'start': '2014-04-27T15:45:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 114,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:49:30+01:00',
                                'start': '2014-04-27T15:46:30+01:00'},
                       'period': {'end': '2014-04-27T15:50:00+01:00',
                                  'start': '2014-04-27T15:45:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 115,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:54:30+01:00',
                                'start': '2014-04-27T15:51:30+01:00'},
                       'period': {'end': '2014-04-27T15:55:00+01:00',
                                  'start': '2014-04-27T15:50:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 115,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:54:30+01:00',
                                'start': '2014-04-27T15:51:30+01:00'},
                       'period': {'end': '2014-04-27T15:55:00+01:00',
                                  'start': '2014-04-27T15:50:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 116,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:59:30+01:00',
                                'start': '2014-04-27T15:56:30+01:00'},
                       'period': {'end': '2014-04-27T16:00:00+01:00',
                                  'start': '2014-04-27T15:55:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 116,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:59:30+01:00',
                                'start': '2014-04-27T15:56:30+01:00'},
                       'period': {'end': '2014-04-27T16:00:00+01:00',
                                  'start': '2014-04-27T15:55:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 117,
             'teams': ['???', '???', '???', None],
             'times': {'game': {'end': '2014-04-27T16:04:30+01:00',
                                'start': '2014-04-27T16:01:30+01:00'},
                       'period': {'end': '2014-04-27T16:05:00+01:00',
                                  'start': '2014-04-27T16:00:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 117,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:04:30+01:00',
                                'start': '2014-04-27T16:01:30+01:00'},
                       'period': {'end': '2014-04-27T16:05:00+01:00',
                                  'start': '2014-04-27T16:00:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 118,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:09:30+01:00',
                                'start': '2014-04-27T16:06:30+01:00'},
                       'period': {'end': '2014-04-27T16:10:00+01:00',
                                  'start': '2014-04-27T16:05:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 118,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:09:30+01:00',
                                'start': '2014-04-27T16:06:30+01:00'},
                       'period': {'end': '2014-04-27T16:10:00+01:00',
                                  'start': '2014-04-27T16:05:00+01:00'}},
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 119,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:19:30+01:00',
                                'start': '2014-04-27T16:16:30+01:00'},
                       'period': {'end': '2014-04-27T16:20:00+01:00',
                                  'start': '2014-04-27T16:15:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 119,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:19:30+01:00',
                                'start': '2014-04-27T16:16:30+01:00'},
                       'period': {'end': '2014-04-27T16:20:00+01:00',
                                  'start': '2014-04-27T16:15:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 120,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:24:30+01:00',
                                'start': '2014-04-27T16:21:30+01:00'},
                       'period': {'end': '2014-04-27T16:25:00+01:00',
                                  'start': '2014-04-27T16:20:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 120,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:24:30+01:00',
                                'start': '2014-04-27T16:21:30+01:00'},
                       'period': {'end': '2014-04-27T16:25:00+01:00',
                                  'start': '2014-04-27T16:20:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 121,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:29:30+01:00',
                                'start': '2014-04-27T16:26:30+01:00'},
                       'period': {'end': '2014-04-27T16:30:00+01:00',
                                  'start': '2014-04-27T16:25:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 121,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:29:30+01:00',
                                'start': '2014-04-27T16:26:30+01:00'},
                       'period': {'end': '2014-04-27T16:30:00+01:00',
                                  'start': '2014-04-27T16:25:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 122,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:34:30+01:00',
                                'start': '2014-04-27T16:31:30+01:00'},
                       'period': {'end': '2014-04-27T16:35:00+01:00',
                                  'start': '2014-04-27T16:30:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 122,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:34:30+01:00',
                                'start': '2014-04-27T16:31:30+01:00'},
                       'period': {'end': '2014-04-27T16:35:00+01:00',
                                  'start': '2014-04-27T16:30:00+01:00'}},
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 123,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:44:30+01:00',
                                'start': '2014-04-27T16:41:30+01:00'},
                       'period': {'end': '2014-04-27T16:45:00+01:00',
                                  'start': '2014-04-27T16:40:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 124,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:49:30+01:00',
                                'start': '2014-04-27T16:46:30+01:00'},
                       'period': {'end': '2014-04-27T16:50:00+01:00',
                                  'start': '2014-04-27T16:45:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 125,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:54:30+01:00',
                                'start': '2014-04-27T16:51:30+01:00'},
                       'period': {'end': '2014-04-27T16:55:00+01:00',
                                  'start': '2014-04-27T16:50:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 126,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:59:30+01:00',
                                'start': '2014-04-27T16:56:30+01:00'},
                       'period': {'end': '2014-04-27T17:00:00+01:00',
                                  'start': '2014-04-27T16:55:00+01:00'}},
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 127,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T17:09:30+01:00',
                                'start': '2014-04-27T17:06:30+01:00'},
                       'period': {'end': '2014-04-27T17:10:00+01:00',
                                  'start': '2014-04-27T17:05:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 128,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T17:14:30+01:00',
                                'start': '2014-04-27T17:11:30+01:00'},
                       'period': {'end': '2014-04-27T17:15:00+01:00',
                                  'start': '2014-04-27T17:10:00+01:00'}},
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 129,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T17:29:30+01:00',
                                'start': '2014-04-27T17:26:30+01:00'},
                       'period': {'end': '2014-04-27T17:30:00+01:00',
                                  'start': '2014-04-27T17:25:00+01:00'}},
             'type': 'knockout'}]]
    eq_(server_get('knockout')['rounds'], ref)
