from __future__ import print_function

from functools import wraps
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


class ApiError(Exception):
    def __init__(self, name, code):
        self.name = name
        self.code = code


def raises_api_error(name, code):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                f(*args, **kwargs)
            except ApiError as e:
                assert e.name == name
                assert e.code == code
            except:
                raise
            else:
                raise AssertionError('Did not raise API error.')
        return wrapper
    return decorator


def server_get(endpoint):
    response, code, header = CLIENT.get(endpoint)
    json_response = json.loads(b''.join(response).decode('UTF-8'))
    code = int(code.split(' ')[0])

    if 200 <= code <= 299:
        return json_response
    elif 400 <= code <= 499:
        assert json_response['error']['code'] == code
        error = json_response['error']
        raise ApiError(error['name'], error['code'])
    else:
        raise AssertionError()  # server error


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
        '/locations',
        '/locations/a-group',
        '/matches',
        '/matches?arena=A',
        '/matches?arena=B',
        '/matches?num=0..1',
        '/matches?arena=B&num=1',
        '/matches?type=knockout',
        '/matches?type=league&limit=10',
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
                          'locations': '/locations',
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


@raises_api_error('NotFound', 404)
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


@raises_api_error('NotFound', 404)
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
                 'display_name': 'B'}})


def test_location():
    eq_(server_get('/locations/a-group'),
        {"description": "A group of some sort, it contains a number of teams.",
         "display_name": "A group",
         "get": "/locations/a-group",
         "shepherds": {"colour": "#A9A9F5",
                       "name": "Blue"},
         "teams": ["BAY", "BDF", "BGS", "BPV", "BRK", "BRN", "BWS", "CCR", \
                   "CGS", "CLF", "CLY", "CPR", "CRB", "DSF", "EMM", "GRD", \
                   "GRS", "GYG", "HRS", "HSO", "HYP", "HZW", "ICE", "JMS", \
                   "KDE", "KES", "KHS", "LFG"]})


@raises_api_error('NotFound', 404)
def test_invalid_location():
    server_get('/locations/nope')


def test_locations():
    a = {"description": "A group of some sort, it contains a number of teams.",
         "display_name": "A group",
         "get": "/locations/a-group",
         "shepherds": {"colour": "#A9A9F5",
                       "name": "Blue"},
         "teams": ["BAY", "BDF", "BGS", "BPV", "BRK", "BRN", "BWS", "CCR", \
                   "CGS", "CLF", "CLY", "CPR", "CRB", "DSF", "EMM", "GRD", \
                   "GRS", "GYG", "HRS", "HSO", "HYP", "HZW", "ICE", "JMS", \
                   "KDE", "KES", "KHS", "LFG"]}
    b = {"display_name": "Another group",
         "get": "/locations/b-group",
         "shepherds": {"colour": "green",
                       "name": "Green"},
         "teams": ["LSS", "MAI", "MAI2", "MEA", "MFG", "NHS", "PAG", "PAS", \
                   "PSC", "QEH", "QMC", "QMS", "RED", "RGS", "RUN", "RWD", \
                   "SCC", "SEN", "SGS", "STA", "SWI", "TBG", "TTN", "TWG", \
                   "WYC"]}

    eq_(server_get('/locations')['locations'], {'a-group': a,
                                                'b-group': b})


def test_team():
    eq_(server_get('/teams/CLF'), {'tla': 'CLF',
                                   'name': 'Clifton High School',
                                   'league_pos': 36,
                                   'location': {'get': '/locations/a-group',
                                                'name': 'a-group'},
                                   'scores': {'league': 68,
                                              'game': 69},
                                   'get': '/teams/CLF'})


def test_team_image():
    eq_(server_get('/teams/BAY')['image_url'], '/teams/BAY/image')


@raises_api_error('NotFound', 404)
def test_no_team_image():
    server_get('/teams/BEES/image')


@raises_api_error('NotFound', 404)
def test_bad_team():
    server_get('/teams/BEES')


def test_matches():
    eq_(server_get('/matches?num=0&arena=A'),
         {'matches': [
           {'num': 0,
            'display_name': 'Match 0',
            'arena': 'A',
            'type': 'league',
            'teams': [None, 'CLY', 'TTN', None],
            'scores': {
               'game': {'CLY': 9, 'TTN': 6},
               'league': {'CLY': 8, 'TTN': 6},
               'ranking': {'CLY': 1, 'TTN': 2},
            },
            'times': {
               'slot': {
                  'start': '2014-04-26T13:00:00+01:00',
                  'end':   '2014-04-26T13:05:00+01:00'
               },
               'game': {
                  'start': '2014-04-26T13:01:30+01:00',
                  'end':   '2014-04-26T13:04:30+01:00'
               },
               'staging': {
                    'opens': '2014-04-26T12:56:30+01:00',
                    'closes':'2014-04-26T12:59:30+01:00',
                    'signal_teams':       '2014-04-26T12:57:30+01:00',
                    'signal_shepherds':   '2014-04-26T12:57:29+01:00',
               },
            }}
         ],
         'last_scored': 99
         })


def test_match_forwards_limit():
    eq_(server_get('/matches?arena=A&limit=1'),
        {'matches': [
            {
                'num': 0,
                'display_name': 'Match 0',
                'arena': 'A',
                'type': 'league',
                'teams': [None, 'CLY', 'TTN', None],
                'scores': {
                    'game': {'CLY': 9, 'TTN': 6},
                    'league': {'CLY': 8, 'TTN': 6},
                    'ranking': {'CLY': 1, 'TTN': 2},
                    },
                'times': {
                    'slot': {
                        'start': '2014-04-26T13:00:00+01:00',
                        'end':   '2014-04-26T13:05:00+01:00'
                    },
                    'game': {
                        'start': '2014-04-26T13:01:30+01:00',
                        'end':   '2014-04-26T13:04:30+01:00'
                    },
                    'staging': {
                        'opens': '2014-04-26T12:56:30+01:00',
                        'closes':'2014-04-26T12:59:30+01:00',
                        'signal_teams':       '2014-04-26T12:57:30+01:00',
                        'signal_shepherds':   '2014-04-26T12:57:29+01:00',
                    },
                }
            }
        ],
        'last_scored': 99})


def test_match_backwards_limit():
    eq_(server_get('/matches?arena=A&limit=-1'),
        {'matches': [
            {
                'display_name': 'Final (#129)',
                'type': 'knockout',
                'num': 129,
                'arena': 'A',
                'times': {
                    'game': {
                        'end': '2014-04-27T17:29:30+01:00',
                        'start': '2014-04-27T17:26:30+01:00'
                    },
                    'slot': {
                        'end': '2014-04-27T17:30:00+01:00',
                        'start': '2014-04-27T17:25:00+01:00'
                    },
                    'staging': {
                        'opens': '2014-04-27T17:21:30+01:00',
                        'closes':'2014-04-27T17:24:30+01:00',
                        'signal_teams':       '2014-04-27T17:22:30+01:00',
                        'signal_shepherds':   '2014-04-27T17:22:29+01:00',
                    }
                },
                'teams': ['???', '???', '???', '???']
            }
        ],
        'last_scored': 99})


@raises_api_error('UnknownMatchFilter', 400)
def test_invalid_match_filter():
    server_get('/matches?number=0&arena=A')


@raises_api_error('BadRequest', 400)
def test_invalid_match_filter_value():
    server_get('/matches?num=&arena=A')


def test_last_scored():
    eq_(server_get('/matches/last_scored'), {'last_scored': 99})


@raises_api_error('BadRequest', 400)
def test_invalid_match_type():
    server_get('/matches?type=bees')


def test_periods():
    eq_(server_get('/periods'),
         {"periods": [
            {
              "type": "league",
              "description": "Saturday, 26 April 2014, afternoon",
              "end_time": "Sat, 26 Apr 2014 16:30:00 GMT",
              "matches": {
                "first_num": 0,
                "last_num": 52,
              },
              "max_end_time": "Sat, 26 Apr 2014 16:40:00 GMT",
              "start_time": "Sat, 26 Apr 2014 12:00:00 GMT"
            },
            {
              "type": "league",
              "description": "Sunday, 27 April 2014, morning",
              "end_time": "Sun, 27 Apr 2014 11:15:00 GMT",
              "matches": {
                "first_num": 53,
                "last_num": 86,
              },
              "max_end_time": "Sun, 27 Apr 2014 11:20:00 GMT",
              "start_time": "Sun, 27 Apr 2014 08:30:00 GMT"
            },
            {
              "type": "league",
              "description": "Sunday, 27 April 2014, afternoon",
              "end_time": "Sun, 27 Apr 2014 14:10:00 GMT",
              "matches": {
                "first_num": 87,
                "last_num": 110,
              },
              "max_end_time": "Sun, 27 Apr 2014 14:10:00 GMT",
              "start_time": "Sun, 27 Apr 2014 12:15:00 GMT"
            },
            {
              "type": "knockout",
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
def test_current_time():
    eq_(server_get('/current')['time'],
        '2014-04-26T13:01:00+01:00')

@freeze_time('2014-04-26 12:30:00', tz_offset=TZ_OFFSET)
def test_current_delay():
    eq_(server_get('/current')['delay'], 15)


@freeze_time('2014-04-26 12:01:00', tz_offset=TZ_OFFSET)
def test_current_match():
    match_list = server_get('/current')['matches']
    match_list.sort(key=lambda match: match['arena'])
    ref = [{'num': 0,
            'display_name': 'Match 0',
            'arena': 'A',
            'type': 'league',
            'teams': [None, 'CLY', 'TTN', None],
            'scores': {
               'game': {'CLY': 9, 'TTN': 6},
               'league': {'CLY': 8, 'TTN': 6},
               'ranking': {'CLY': 1, 'TTN': 2},
            },
            'times': {
               'slot': {
                  'start': '2014-04-26T13:00:00+01:00',
                  'end':   '2014-04-26T13:05:00+01:00'
               },
               'game': {
                  'start': '2014-04-26T13:01:30+01:00',
                  'end':   '2014-04-26T13:04:30+01:00'
               },
               'staging': {
                  'opens': '2014-04-26T12:56:30+01:00',
                  'closes':'2014-04-26T12:59:30+01:00',
                  'signal_teams':       '2014-04-26T12:57:30+01:00',
                  'signal_shepherds':   '2014-04-26T12:57:29+01:00',
               }
            }},
           {'num': 0,
            'display_name': 'Match 0',
            'arena': 'B',
            'type': 'league',
            'teams': ['GRS', 'QMC', None, None],
            'scores': {
               'game': {'QMC': 3, 'GRS': 5},
               'league': {'QMC': 6, 'GRS': 8},
               'ranking': {'QMC': 2, 'GRS': 1},
            },
            'times': {
               'slot': {
                  'start': '2014-04-26T13:00:00+01:00',
                  'end':   '2014-04-26T13:05:00+01:00'
               },
               'game': {
                  'start': '2014-04-26T13:01:30+01:00',
                  'end':   '2014-04-26T13:04:30+01:00'
               },
               'staging': {
                  'opens': '2014-04-26T12:56:30+01:00',
                  'closes':'2014-04-26T12:59:30+01:00',
                  'signal_teams':       '2014-04-26T12:57:30+01:00',
                  'signal_shepherds':   '2014-04-26T12:57:29+01:00',
               },
            }}]
    eq_(match_list, ref)


def test_knockouts():
    import pprint
    ref = [[{'arena': 'A',
             'num': 111,
             'display_name': 'Match 111',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 111,
             'display_name': 'Match 111',
             'teams': [None, '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 112,
             'display_name': 'Match 112',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 112,
             'display_name': 'Match 112',
             'teams': ['???', '???', '???', None],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 113,
             'display_name': 'Match 113',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 113,
             'display_name': 'Match 113',
             'teams': ['???', '???', '???', None],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 114,
             'display_name': 'Match 114',
             'teams': ['???', '???', None, '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 114,
             'display_name': 'Match 114',
             'teams': ['???', None, '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 115,
             'display_name': 'Match 115',
             'teams': ['???', None, '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 115,
             'display_name': 'Match 115',
             'teams': [None, '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 116,
             'display_name': 'Match 116',
             'teams': [None, '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 116,
             'display_name': 'Match 116',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 117,
             'display_name': 'Match 117',
             'teams': [None, '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 117,
             'display_name': 'Match 117',
             'teams': ['???', '???', '???', None],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 118,
             'display_name': 'Match 118',
             'teams': [None, '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 118,
             'display_name': 'Match 118',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 119,
             'display_name': 'Match 119',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 119,
             'display_name': 'Match 119',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 120,
             'display_name': 'Match 120',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 120,
             'display_name': 'Match 120',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 121,
             'display_name': 'Match 121',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 121,
             'display_name': 'Match 121',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 122,
             'display_name': 'Match 122',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'B',
             'num': 122,
             'display_name': 'Match 122',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 123,
             'display_name': 'Quarter 1 (#123)',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 124,
             'display_name': 'Quarter 2 (#124)',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 125,
             'display_name': 'Quarter 3 (#125)',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 126,
             'display_name': 'Quarter 4 (#126)',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 127,
             'display_name': 'Semi 1 (#127)',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'},
            {'arena': 'A',
             'num': 128,
             'display_name': 'Semi 2 (#128)',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'}],
           [{'arena': 'A',
             'num': 129,
             'display_name': 'Final (#129)',
             'teams': ['???', '???', '???', '???'],
             'times': None,
             'type': 'knockout'}]]
    actual_rounds = server_get('knockout')['rounds']

    times_keys = ['game', 'slot', 'staging']
    for r in actual_rounds:
        for m in r:
            assert 'times' in m
            keys = list(sorted(m['times'].keys()))
            assert times_keys == keys, "Wrong time keys in {0}.".format(m)
            m['times'] = None

    # Our own assertion since the built-in ones don't cope with such a
    # large structure very well (ie, the failure output sucks)
    for r_num, matches in enumerate(ref):

        assert r_num < len(actual_rounds), "Failed to get round '{0}' from server".format(r_num)

        actual_matches = actual_rounds[r_num]

        for m_num, match in enumerate(matches):

            assert m_num < len(actual_matches), \
                "Failed to get match '{0}' within round '{1}' from server".format(m_num, r_num)

            actual_match = actual_matches[m_num]

            print(match, actual_match)

            assert match == actual_match, \
                "Round: {}, Match: {} (#{})".format(r_num, m_num, match['num'])

    # Just in case the above is faulty
    eq_(actual_rounds, ref)


@raises_api_error('NotFound', 404)
def test_tiebreaker():
    server_get('/tiebreaker')
