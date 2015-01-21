
import datetime
from dateutil.tz import tzlocal

def match_json_info(comp, match):
    if match:
        match_period_lengths = comp.schedule.match_period_lengths

        info = {
            "num": match.num,
            "arena": match.arena,
            "teams": match.teams,
            "type": match.type,
            "times": {
                "period": {
                    "start": match.start_time.isoformat(),
                    "end": match.end_time.isoformat()
                },
                "game": {
                    "start": (match.start_time + match_period_lengths['pre']).isoformat(),
                    "end": (match.end_time + match_period_lengths['pre'] + match_period_lengths['match']).isoformat()
                }
            }
        }

        league = comp.scores.league
        k = (match.arena, match.num)
        if k in league.game_points:
            info["scores"] = {
                "game": league.game_points[k],
                "league": league.ranked_points[k]
            }

        return info
    else:
        return {
            "error": True,
            "msg": "No match at this time."
        }

def match_parse_name(schedule, arena, s):
    matches = schedule.matches

    try:
        "First try it as in integer"
        n = int(s)
    except ValueError:
        pass
    else:
        return matches[n][arena]

    def get_next():
        now = datetime.datetime.now(tzlocal())
        return schedule.match_after(arena, now)

    def get_bounded(n):
        if n < 0:
            return None
        try:
            return matches[n][arena]
        except (IndexError, KeyError):
            return None

    if s == "previous":
        current = schedule.current_match(arena)
        if current is None:
            "between sessions (etc.)"
            current = get_next()
        if current is None:
            "after the competition"
            return None
        return get_bounded(current.num - 1)

    if s == "current":
        return schedule.current_match(arena)

    if s == "next":
        return get_next()

    if s.startswith("next+"):
        value = int(s[5:])
        next_m = get_next()
        if next_m is None:
            "after the competition"
            return None
        return get_bounded(next_m.num + value)

    raise ValueError
