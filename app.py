#!/usr/bin/env python
import datetime
import os
from flask import g, Flask, jsonify, json, request
from srcomp import SRComp
from srcomp.matches import KNOCKOUT_MATCH
import time

app = Flask(__name__)

class SRCompManager(object):
    def __init__(self):
        self.root_dir = "./"
        self.update_time = None

    def _load(self):
        self.comp = SRComp(self.root_dir)
        self.update_time = time.time()

    def get_comp(self):
        if self.update_time is None:
            self._load()

        elif time.time() - self.update_time > 5:
            "Data is more than 5 seconds old -- reload"
            self._load()

        return self.comp

comp_man = SRCompManager()

@app.before_request
def before_request():
    if "COMPSTATE" in app.config:
        comp_man.root_dir = app.config["COMPSTATE"]
    g.comp_man = comp_man

@app.after_request
def after_request(resp):
    if 'Origin' in request.headers:
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

def match_json_info(comp, match):
    if match:
        info = {
            "number": match.num,
            "arena": match.arena,
            "teams": match.teams,
            "start_time": match.start_time.isoformat(),
            "end_time": match.end_time.isoformat(),
        }

        league = comp.scores.league
        k = (match.arena, match.num)
        if k in league.game_points:
            info["scores"] = {
                "game": league.game_points[k],
                "league": league.match_league_points[k]
            }

        return info
    else:
        return {
            "error": True,
            "msg": "No match at this time."
        }

def match_parse_name(comp, arena, s):
    matches = comp.schedule.matches

    try:
        "First try it as in integer"
        n = int(s)
    except ValueError:
        pass
    else:
        return matches[n][arena]

    if s == "current":
        return comp.schedule.current_match(arena)

    if s == "next":
        now = datetime.datetime.utcnow()
        return comp.schedule.match_after(arena, now)

    if s == "next+1":
        now = datetime.datetime.utcnow()
        next_m = comp.schedule.match_after(arena, now)

        n = next_m.num + 1
        if n >= len(matches):
            "No next+1 match"
            return None

        return matches[n][arena]

    raise ValueError

@app.route("/matches/<arena>", methods=["GET"])
def match_query(arena):
    comp = g.comp_man.get_comp()

    if "numbers" in request.args:
        result = []

        for desc in request.args["numbers"].split(","):
            try:
                m = match_parse_name(comp, arena, desc)
            except (IndexError, ValueError):
                return jsonify(error=True,
                               msg="Unknown match '{0}'".format(desc)), 400
            info = match_json_info(comp, m)
            info["query"] = desc
            result.append(info)

        return jsonify(matches=result)
    return jsonify(error=True), 400

@app.route("/matches/<arena>/<int:match_number>")
def match_info(arena, match_number):
    "Get information about the given match number"
    comp = g.comp_man.get_comp()

    if match_number < 0 or match_number > len(comp.schedule.matches):
        return jsonify(error=True,msg="Invalid match number"), 404
    match = comp.schedule.matches[match_number]

    if arena not in match:
        return jsonify(error=True,msg="Invalid arena"), 404
    match = match[arena]

    return jsonify(**match_json_info(comp, match))

@app.route("/matches/<arena>/<int:match_number_min>-<int:match_number_max>")
def match_info_range(arena, match_number_min, match_number_max):
    "Get information about the given range of matches"
    comp = g.comp_man.get_comp()
    resp = {}

    match_number_min = max(match_number_min, 0)
    match_number_max = min(match_number_max, len(comp.schedule.matches)-1)

    for match_n in range(match_number_min, match_number_max+1):
        resp[match_n] = match_json_info(comp, comp.schedule.matches[match_n][arena])

    return jsonify(matches = resp)

@app.route("/matches/all")
def match_info_all():
    "Get information about all the scheduled matches"
    comp = g.comp_man.get_comp()

    return jsonify(matches = comp.schedule.matches)

@app.route("/matches/periods")
def match_info_periods():
    "Get information about all the scheduled matches, organised by period"
    comp = g.comp_man.get_comp()

    return jsonify(periods = comp.schedule.match_periods)

@app.route("/matches/knockouts")
def knockout_matches():
    "Get information about all the knockout matches"
    comp = g.comp_man.get_comp()

    started = False
    for arena in comp.arenas:
        current = comp.schedule.current_match(arena)
        if current is not None:
            started = current["type"] == KNOCKOUT_MATCH

    return jsonify(rounds = comp.schedule.knockout_rounds,
                   started = started)

@app.route("/matches/<arena>/current")
def current_match_info(arena):
    comp = g.comp_man.get_comp()
    current = comp.schedule.current_match(arena)

    if current is None:
        return jsonify(number=None, msg="No current match")

    return jsonify(**match_json_info(comp, current))

@app.route("/teams")
def teams():
    comp = g.comp_man.get_comp()

    resp = {}
    for team in comp.teams.values():
        resp[team.tla] = team.name

    return jsonify(teams = resp)

@app.route("/scores/league")
def scores():
    comp = g.comp_man.get_comp()

    league = {}
    game = {}
    for tla, pts in comp.scores.league.teams.items():
        league[tla] = pts.league_points
        game[tla] = pts.game_points

    return jsonify(league_points=league, game_points=game, \
                    last_scored=comp.scores.league.last_scored_match)

@app.route("/arenas")
def arenas():
    comp = g.comp_man.get_comp()

    return jsonify(arenas = comp.arenas)

@app.route("/corner/<int:number>")
def corner(number):
    comp = g.comp_man.get_comp()

    if number not in comp.corners:
        return jsonify(error=True,msg="Invalid corner"), 404

    return jsonify(colour = comp.corners[number].colour)

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser( description = "SR Competition info API HTTP server" )
    parser.add_argument("compstate", help = "Competition state git repository path")
    parser.add_argument("-p", "--port", type=int, default=5112,
                        help = "Port to listen on")
    parser.add_argument("--no-reloader", action="store_false", default=True,
                        dest="reloader", help = "Disable the reloader")
    args = parser.parse_args()

    app.config["COMPSTATE"] = args.compstate
    app.debug = True
    app.run(host='0.0.0.0', port=args.port, use_reloader=args.reloader)
