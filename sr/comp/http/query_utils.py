
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
                    "end": (match.start_time + match_period_lengths['pre'] + match_period_lengths['match']).isoformat()
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
