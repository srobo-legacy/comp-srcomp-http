#!/usr/bin/env python
import os
from flask import g, Flask, jsonify, json
from srcomp import SRComp
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

def match_json_info(comp, match):
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

@app.route("/matches/<arena>/<int:match_number>")
def match_info(arena, match_number):
    "Get information about the given match number"
    comp = g.comp_man.get_comp()

    if match_number not in comp.schedule.matches:
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

    for match_n in range(match_number_min, match_number_max+1):
        if match_n not in comp.schedule.matches:
            "Skip matches that don't exist"
            continue

        resp[match_n] = match_json_info(comp, comp.schedule.matches[match_n][arena])

    return jsonify(matches = resp)

@app.route("/matches/all")
def match_info_all():
    "Get information about the given range of matches"
    comp = g.comp_man.get_comp()

    return jsonify(matches = comp.schedule.matches)

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

    return jsonify(league_points=league, game_points=game)

@app.route("/arenas")
def arenas():
    comp = g.comp_man.get_comp()

    return jsonify(arenas = comp.arenas)

@app.route("/knockout/max_entrants")
def knockout_entrants():
    comp = g.comp_man.get_comp()

    return jsonify(max_entrants = comp.knockout.max_entrants)

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
