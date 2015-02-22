
import datetime
from dateutil.tz import tzlocal

def match_json_info(comp, match):
    if match:
        match_slot_lengths = comp.schedule.match_slot_lengths

        info = {
            "num": match.num,
            "arena": match.arena,
            "teams": match.teams,
            "type": match.type.value,
            "times": {
                "slot": {
                    "start": match.start_time.isoformat(),
                    "end": match.end_time.isoformat()
                },
                "game": {
                    "start": (match.start_time + match_slot_lengths['pre']).isoformat(),
                    "end": (match.start_time + match_slot_lengths['pre'] + match_slot_lengths['match']).isoformat()
                }
            }
        }

        k = (match.arena, match.num)

        league = comp.scores.league
        if k in league.game_points:
            info["scores"] = {
                "game": league.game_points[k],
                "league": league.ranked_points[k]
            }

        knockout = comp.scores.knockout
        if k in knockout.game_points:
            info["scores"] = { "game": knockout.game_points[k] }

        return info
    else:
        return {
            "error": True,
            "msg": "No match at this time."
        }

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
