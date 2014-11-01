
import datetime
import mock

from srcomp.matches import MatchSchedule, Match, LEAGUE_MATCH
from sr.comp.http.query_utils import match_parse_name

def dtime(hour, minute, second = 0):
    return datetime.datetime(2014, 3, 26,  hour, minute, second)

def get_basic_data():
    the_data = {
        "match_period_length_seconds": 300,
        "delays": [ {
            "delay": 60,
            "time":  dtime(13, 2)
        } ],
        "match_periods": {
            "league": [ {
                "description": "A description of the period",
                "start_time":   dtime(13,  0),
                "end_time":     dtime(13, 30),
                "max_end_time": dtime(13, 40)
            } ],
            "knockout": []
        },
        "matches": {
            0: {
                "A": ["0A"],
                "B": ["0B"]
            },
            1: {
                "A": ["1A"],
                "B": ["1B"]
            },
            2: {
                "A": ["2A"]
            }
        }
    }
    return the_data

def load_data(the_data):
    matches = MatchSchedule(the_data)
    return matches

def load_basic_data():
    matches = load_data(get_basic_data())
    assert len(matches.match_periods) == 1
    assert len(matches.matches) == 3
    return matches


def helper(expected_match, at_time, input_str):
    schedule = load_basic_data()

    now_mock = mock.Mock(return_value = at_time)
    dt_dt_mock = mock.Mock(now = now_mock)
    dt_mock = mock.Mock(datetime = dt_dt_mock)

    with mock.patch('sr.comp.http.query_utils.datetime', dt_mock), \
            mock.patch('srcomp.matches.datetime', dt_mock):
        match = match_parse_name(schedule, 'A', input_str)

        assert expected_match == match, "Wrong match returned for '{0}'.".format(input_str)

FIRST_MATCH = Match(0, 'A', ["0A"], dtime(13, 0), dtime(13, 5), LEAGUE_MATCH)
SECOND_MATCH = Match(1, 'A', ["1A"], dtime(13, 6), dtime(13, 11), LEAGUE_MATCH)
THIRD_MATCH = Match(2, 'A', ["2A"], dtime(13, 11), dtime(13, 16), LEAGUE_MATCH)


def test_previous_before_first():
    then = dtime(12, 30)
    helper(None, then, 'previous')

def test_previous_during_first():
    then = dtime(13, 1)
    helper(None, then, 'previous')

def test_previous_during_delay():
    then = dtime(13, 5, 30)
    helper(FIRST_MATCH, then, 'previous')

def test_previous_during_second():
    then = dtime(13, 7)
    helper(FIRST_MATCH, then, 'previous')

def test_previous_during_last():
    then = dtime(13, 14)
    helper(SECOND_MATCH, then, 'previous')

def test_previous_after_last():
    # NB: this value doesn't quite feel right -- is there a reason
    # not to return the final match?
    then = dtime(17, 0)
    helper(None, then, 'previous')


def test_current_before_first():
    then = dtime(12, 30)
    helper(None, then, 'current')

def test_current_during_first():
    then = dtime(13, 1)
    helper(FIRST_MATCH, then, 'current')

def test_current_during_delay():
    then = dtime(13, 5, 30)
    helper(None, then, 'current')

def test_current_during_last():
    then = dtime(13, 14)
    helper(THIRD_MATCH, then, 'current')

def test_current_after_last():
    then = dtime(14, 0)
    helper(None, then, 'current')


def test_next_before_first():
    then = dtime(12, 30)
    helper(FIRST_MATCH, then, 'next')

def test_next_during_first():
    then = dtime(13, 1)
    helper(SECOND_MATCH, then, 'next')

def test_next_during_delay():
    then = dtime(13, 5, 30)
    helper(SECOND_MATCH, then, 'next')

def test_next_during_second():
    then = dtime(13, 7)
    helper(THIRD_MATCH, then, 'next')

def test_next_during_last():
    then = dtime(13, 14)
    helper(None, then, 'next')

def test_next_after_last():
    then = dtime(17, 0)
    helper(None, then, 'next')


def test_next_1_before_first():
    then = dtime(12, 30)
    helper(SECOND_MATCH, then, 'next+1')

def test_next_1_during_first():
    then = dtime(13, 1)
    helper(THIRD_MATCH, then, 'next+1')

def test_next_1_during_delay():
    then = dtime(13, 5, 30)
    helper(THIRD_MATCH, then, 'next+1')

def test_next_1_during_second():
    then = dtime(13, 7)
    helper(None, then, 'next+1')

def test_next_1_during_last():
    then = dtime(13, 14)
    helper(None, then, 'next+1')

def test_next_1_after_last():
    then = dtime(17, 0)
    helper(None, then, 'next+1')


def test_next_2_before_first():
    then = dtime(12, 30)
    helper(THIRD_MATCH, then, 'next+2')

def test_next_2_during_first():
    then = dtime(13, 1)
    helper(None, then, 'next+2')

def test_next_2_during_delay():
    then = dtime(13, 5, 30)
    helper(None, then, 'next+2')

def test_next_2_during_second():
    then = dtime(13, 7)
    helper(None, then, 'next+2')

def test_next_2_during_last():
    then = dtime(13, 14)
    helper(None, then, 'next+2')

def test_next_2_after_last():
    then = dtime(17, 0)
    helper(None, then, 'next+2')

