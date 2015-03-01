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

# Work around a bug in freezegun where the timezone handling is different
# in Python 2 than 3. From what I can tell it's the Python 3 which is wrong,
# but it doesn't really matter; we just need to work around it.
TZ_OFFSET = 0
import sys
if sys.version_info[0] == 3:
    TZ_OFFSET = 1

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
        '/matches/last_scored',
        '/periods',
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
                          'periods': '/periods',
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
    eq_(cfg['match_slots'], {'pre': 90,
                             'match': 180,
                             'post': 30,
                             'total': 300})

def test_arena():
    eq_(server_get('/arenas/A'), {'get': '/arenas/A',
                                  'name': 'A',
                                  'colour': '#ff0000',
                                  'display_name': 'A'})

@raises(API404Error)
def test_invalid_arena():
    server_get('/arenas/Z')

def test_arenas():
    eq_(server_get('/arenas')['arenas'],
          {'A': {'get': '/arenas/A',
                 'name': 'A',
                 'colour': '#ff0000',
                 'display_name': 'A'},
           'B': {'get': '/arenas/B',
                 'name': 'B',
                 'colour': '#00ff00',
                 'display_name': 'B'}})

def test_team():
    eq_(server_get('/teams/CLF'), {'tla': 'CLF',
                                   'name': 'Clifton High School',
                                   'league_pos': 36,
                                   'scores': {'league': 68,
                                              'game': 69},
                                   'get': '/teams/CLF'})


def test_team_image():
    eq_(server_get('/teams/BAY')['image_url'], '/teams/BAY/image')


@raises(API404Error)
def test_no_team_image():
    server_get('/teams/BEES/image')


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
               'slot': {
                  'start': '2014-04-26T13:00:00+01:00',
                  'end':   '2014-04-26T13:05:00+01:00'
               },
               'game': {
                  'start': '2014-04-26T13:01:30+01:00',
                  'end':   '2014-04-26T13:04:30+01:00'
               }
            }}
         ],
         'last_scored': 99
         })

def test_last_scored():
    eq_(server_get('/matches/last_scored'), {'last_scored': 99})

@raises(APIError)
def test_invalid_match_type():
    server_get('/matches?type=bees')

def test_periods():
    eq_(server_get('/periods'),
         {"periods": [
            {
              "description": "Saturday, 26 April 2014, afternoon",
              "end_time": "Sat, 26 Apr 2014 16:30:00 GMT",
              "matches": {
                "first_num": 0,
                "last_num": 54
              },
              "max_end_time": "Sat, 26 Apr 2014 16:40:00 GMT",
              "start_time": "Sat, 26 Apr 2014 12:00:00 GMT"
            },
            {
              "description": "Sunday, 27 April 2014, morning",
              "end_time": "Sun, 27 Apr 2014 11:15:00 GMT",
              "matches": {
                "first_num": 55,
                "last_num": 88
              },
              "max_end_time": "Sun, 27 Apr 2014 11:20:00 GMT",
              "start_time": "Sun, 27 Apr 2014 08:30:00 GMT"
            },
            {
              "description": "Sunday, 27 April 2014, afternoon",
              "end_time": "Sun, 27 Apr 2014 14:00:00 GMT",
              "matches": {
                "first_num": 89,
                "last_num": 110
              },
              "max_end_time": "Sun, 27 Apr 2014 14:00:00 GMT",
              "start_time": "Sun, 27 Apr 2014 12:15:00 GMT"
            },
            {
              "description": "The Knockouts, Sunday, 27 April 2014, afternoon",
              "end_time": "Sun, 27 Apr 2014 16:30:00 GMT",
              "matches": {
                "first_num": 111,
                "last_num": 129
              },
              "max_end_time": "Sun, 27 Apr 2014 16:30:00 GMT",
              "start_time": "Sun, 27 Apr 2014 14:30:00 GMT"
            }
          ]
        })

@freeze_time('2014-04-26 12:01:00', tz_offset=TZ_OFFSET)
def test_current_match_time():
    eq_(server_get('/current')['time'],
        '2014-04-26T13:01:00+01:00')

@freeze_time('2014-04-26 12:01:00', tz_offset=TZ_OFFSET)
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
               'slot': {
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
               'slot': {
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
                       'slot': {'end': '2014-04-27T15:35:00+01:00',
                                'start': '2014-04-27T15:30:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 111,
             'teams': ['???', '???', '???', None],
             'times': {'game': {'end': '2014-04-27T15:34:30+01:00',
                                'start': '2014-04-27T15:31:30+01:00'},
                       'slot': {'end': '2014-04-27T15:35:00+01:00',
                                'start': '2014-04-27T15:30:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 112,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:39:30+01:00',
                                'start': '2014-04-27T15:36:30+01:00'},
                       'slot': {'end': '2014-04-27T15:40:00+01:00',
                                'start': '2014-04-27T15:35:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 112,
             'teams': ['???', '???', None, '???'],
             'times': {'game': {'end': '2014-04-27T15:39:30+01:00',
                                'start': '2014-04-27T15:36:30+01:00'},
                       'slot': {'end': '2014-04-27T15:40:00+01:00',
                                'start': '2014-04-27T15:35:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 113,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:44:30+01:00',
                                'start': '2014-04-27T15:41:30+01:00'},
                       'slot': {'end': '2014-04-27T15:45:00+01:00',
                                'start': '2014-04-27T15:40:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 113,
             'teams': [None, '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:44:30+01:00',
                                'start': '2014-04-27T15:41:30+01:00'},
                       'slot': {'end': '2014-04-27T15:45:00+01:00',
                                'start': '2014-04-27T15:40:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 114,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:49:30+01:00',
                                'start': '2014-04-27T15:46:30+01:00'},
                       'slot': {'end': '2014-04-27T15:50:00+01:00',
                                'start': '2014-04-27T15:45:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 114,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:49:30+01:00',
                                'start': '2014-04-27T15:46:30+01:00'},
                       'slot': {'end': '2014-04-27T15:50:00+01:00',
                                'start': '2014-04-27T15:45:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 115,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:54:30+01:00',
                                'start': '2014-04-27T15:51:30+01:00'},
                       'slot': {'end': '2014-04-27T15:55:00+01:00',
                                'start': '2014-04-27T15:50:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 115,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:54:30+01:00',
                                'start': '2014-04-27T15:51:30+01:00'},
                       'slot': {'end': '2014-04-27T15:55:00+01:00',
                                'start': '2014-04-27T15:50:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 116,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:59:30+01:00',
                                'start': '2014-04-27T15:56:30+01:00'},
                       'slot': {'end': '2014-04-27T16:00:00+01:00',
                                  'start': '2014-04-27T15:55:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 116,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T15:59:30+01:00',
                                'start': '2014-04-27T15:56:30+01:00'},
                       'slot': {'end': '2014-04-27T16:00:00+01:00',
                                'start': '2014-04-27T15:55:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 117,
             'teams': ['???', '???', '???', None],
             'times': {'game': {'end': '2014-04-27T16:04:30+01:00',
                                'start': '2014-04-27T16:01:30+01:00'},
                       'slot': {'end': '2014-04-27T16:05:00+01:00',
                                'start': '2014-04-27T16:00:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 117,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:04:30+01:00',
                                'start': '2014-04-27T16:01:30+01:00'},
                       'slot': {'end': '2014-04-27T16:05:00+01:00',
                                'start': '2014-04-27T16:00:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 118,
             'teams': ['???', None, '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:09:30+01:00',
                                'start': '2014-04-27T16:06:30+01:00'},
                       'slot': {'end': '2014-04-27T16:10:00+01:00',
                                'start': '2014-04-27T16:05:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 118,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:09:30+01:00',
                                'start': '2014-04-27T16:06:30+01:00'},
                       'slot': {'end': '2014-04-27T16:10:00+01:00',
                                'start': '2014-04-27T16:05:00+01:00'}},
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 119,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:19:30+01:00',
                                'start': '2014-04-27T16:16:30+01:00'},
                       'slot': {'end': '2014-04-27T16:20:00+01:00',
                                'start': '2014-04-27T16:15:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 119,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:19:30+01:00',
                                'start': '2014-04-27T16:16:30+01:00'},
                       'slot': {'end': '2014-04-27T16:20:00+01:00',
                                  'start': '2014-04-27T16:15:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 120,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:24:30+01:00',
                                'start': '2014-04-27T16:21:30+01:00'},
                       'slot': {'end': '2014-04-27T16:25:00+01:00',
                                'start': '2014-04-27T16:20:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 120,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:24:30+01:00',
                                'start': '2014-04-27T16:21:30+01:00'},
                       'slot': {'end': '2014-04-27T16:25:00+01:00',
                                'start': '2014-04-27T16:20:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 121,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:29:30+01:00',
                                'start': '2014-04-27T16:26:30+01:00'},
                       'slot': {'end': '2014-04-27T16:30:00+01:00',
                                'start': '2014-04-27T16:25:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 121,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:29:30+01:00',
                                'start': '2014-04-27T16:26:30+01:00'},
                       'slot': {'end': '2014-04-27T16:30:00+01:00',
                                'start': '2014-04-27T16:25:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 122,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:34:30+01:00',
                                'start': '2014-04-27T16:31:30+01:00'},
                       'slot': {'end': '2014-04-27T16:35:00+01:00',
                                'start': '2014-04-27T16:30:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'B',
             'num': 122,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:34:30+01:00',
                                'start': '2014-04-27T16:31:30+01:00'},
                       'slot': {'end': '2014-04-27T16:35:00+01:00',
                                'start': '2014-04-27T16:30:00+01:00'}},
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 123,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:44:30+01:00',
                                'start': '2014-04-27T16:41:30+01:00'},
                       'slot': {'end': '2014-04-27T16:45:00+01:00',
                                'start': '2014-04-27T16:40:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 124,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:49:30+01:00',
                                'start': '2014-04-27T16:46:30+01:00'},
                       'slot': {'end': '2014-04-27T16:50:00+01:00',
                                'start': '2014-04-27T16:45:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 125,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:54:30+01:00',
                                'start': '2014-04-27T16:51:30+01:00'},
                       'slot': {'end': '2014-04-27T16:55:00+01:00',
                                'start': '2014-04-27T16:50:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 126,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T16:59:30+01:00',
                                'start': '2014-04-27T16:56:30+01:00'},
                       'slot': {'end': '2014-04-27T17:00:00+01:00',
                                'start': '2014-04-27T16:55:00+01:00'}},
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 127,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T17:09:30+01:00',
                                'start': '2014-04-27T17:06:30+01:00'},
                       'slot': {'end': '2014-04-27T17:10:00+01:00',
                                'start': '2014-04-27T17:05:00+01:00'}},
             'type': 'knockout'},
            {'arena': 'A',
             'num': 128,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T17:14:30+01:00',
                                'start': '2014-04-27T17:11:30+01:00'},
                       'slot': {'end': '2014-04-27T17:15:00+01:00',
                                'start': '2014-04-27T17:10:00+01:00'}},
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 129,
             'teams': ['???', '???', '???', '???'],
             'times': {'game': {'end': '2014-04-27T17:29:30+01:00',
                                'start': '2014-04-27T17:26:30+01:00'},
                       'slot': {'end': '2014-04-27T17:30:00+01:00',
                                'start': '2014-04-27T17:25:00+01:00'}},
             'type': 'knockout'}]]
    actual_rounds = server_get('knockout')['rounds']

    # Our own assertion since the built-in ones don't cope with such a
    # large structure very well (ie, the failure output sucks)
    for r_num, matches in enumerate(ref):

        assert r_num < len(actual_rounds), "Failed to get round '{0}' from server".format(r_num)

        actual_matches = actual_rounds[r_num]

        for m_num, match in enumerate(matches):

            assert m_num < len(actual_matches), \
                "Failed to get match '{0}' within round '{1}' from server".format(m_num, r_num)

            actual_match = actual_matches[m_num]

            assert match == actual_match, "Round: {0}, match: {1}".format(r_num, m_num)

    # Just in case the above is faulty
    eq_(actual_rounds, ref)
