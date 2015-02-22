import mock

from sr.comp.http.query_utils import get_scores
from sr.comp.match_period import Match

GAME_POINTS_DUMMY = 'test game_points for: '
POSITIONS_DUMMY = 'test positions for: '
RANKED_DUMMY = 'test ranked for: '

def make_session_scores(arena, num):
    key = (arena, num)
    scores = mock.Mock()
    scores.game_points = {key: GAME_POINTS_DUMMY + str(key)}
    scores.game_positions = {key: POSITIONS_DUMMY + str(key)}
    scores.ranked_points = {key: RANKED_DUMMY + str(key)}
    return scores

def build_scores():
    scores = mock.Mock()
    scores.league = make_session_scores('A', 0)
    scores.knockout = make_session_scores('A', 1)
    return scores

def build_match(num, arena, teams = None, start_time = None, \
                end_time = None, type_ = None):
    return Match(num, arena, teams, start_time, end_time, type_)

def test_league_match():
    scores = build_scores()
    info = get_scores(scores, build_match(num=0, arena='A'))
    expected = {
        "game": GAME_POINTS_DUMMY + "('A', 0)",
        "league": RANKED_DUMMY + "('A', 0)"
    }
    assert expected == info

def test_knockout_match():
    scores = build_scores()
    info = get_scores(scores, build_match(num=1, arena='A'))
    expected = {
        "game": GAME_POINTS_DUMMY + "('A', 1)"
    }
    assert expected == info

def test_no_match():
    scores = build_scores()
    info = get_scores(scores, build_match(num=1, arena='B'))
    expected = None
    assert expected == info
