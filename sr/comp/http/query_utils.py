"""Various utils for working with HTTP."""

from sr.comp.match_period import MatchType

def get_scores(scores, match):
    """
    Get a scores object suitable for JSON output.

    Parameters
    ----------
    scores : sr.comp.scores.Scores
        The competition scores.
    match : sr.comp.match_period.Match
        A match.

    Returns
    -------
    dict
        A dictionary suitable for JSON output.
    """
    k = (match.arena, match.num)

    def degroup(grouped_positions):
        positions = {}
        for pos, teams in grouped_positions.items():
            for tla in teams:
                positions[tla] = pos
        return positions

    def get_scores_info(match):
        if match.type == MatchType.knockout:
            return scores.knockout
        elif match.type == MatchType.tiebreaker:
            return scores.tiebreaker
        else:
            return None

    scores_info = get_scores_info(match)
    if scores_info and k in scores_info.game_points:
        return {
            "game": scores_info.game_points[k],
            "normalised": scores_info.ranked_points[k],
            "ranking": degroup(scores_info.game_positions[k]),
        }

    # TODO: consider using 'normalised' for both, instead of 'league' below
    league = scores.league
    if k in league.game_points:
        return {
            "game": league.game_points[k],
            "league": league.ranked_points[k],
            "ranking": degroup(league.game_positions[k]),
        }

    return None


def match_json_info(comp, match):
    """
    Get match JSON information.

    Parameters
    ----------
    comp : sr.comp.comp.SRComp
        A competition instance.
    match : sr.comp.match_periods.Match
        A match.

    Returns
    -------
    dict
        A :class:`dict` containing JSON suitable output.
    """
    match_slot_lengths = comp.schedule.match_slot_lengths

    info = {
        "num": match.num,
        'display_name': match.display_name,
        "arena": match.arena,
        "teams": match.teams,
        "type": match.type.value,
        "times": {
            "slot": {
                "start": match.start_time.isoformat(),
                "end": match.end_time.isoformat()
            },
            "game": {
                "start": (match.start_time +
                          match_slot_lengths['pre']).isoformat(),
                "end": (match.start_time +
                        match_slot_lengths['pre'] +
                        match_slot_lengths['match']).isoformat()
            }
        }
    }

    score_info = get_scores(comp.scores, match)
    if score_info:
        info['scores'] = score_info

    return info


def parse_difference_string(string, type_converter=int):
    """
    Parse a difference string (x..x, ..x, x.., x) and return a function that
    accepts a single argument and returns ``True`` if it is in the difference.
    """
    separator = '..'
    if string == separator:
        raise ValueError('Must specify at least one bound.')
    tokens = string.split(separator)

    if len(tokens) > 2:
        raise ValueError('Argument is not a different string.')
    elif len(tokens) == 1:
        converted_token = type_converter(tokens[0])
        return lambda x: x == converted_token
    elif len(tokens) == 2:
        if not tokens[1]:
            lower_bound = type_converter(tokens[0])
            return lambda x: x >= lower_bound
        elif not tokens[0]:
            upper_bound = type_converter(tokens[1])
            return lambda x: x <= upper_bound
        else:
            lhs = type_converter(tokens[0])
            rhs = type_converter(tokens[1])
            if lhs > rhs:
                raise ValueError('Bounds are the wrong way around.')
            return lambda x: lhs <= x <= rhs
    else:
        raise AssertionError('Argument contains unknown input.')
