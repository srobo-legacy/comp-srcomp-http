
from flask import g, Flask, jsonify, request, url_for

from sr.comp.http.manager import SRCompManager
from sr.comp.http.query_utils import match_json_info, match_parse_name

app = Flask(__name__)

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

@app.route('/')
def root():
    return jsonify(arenas=url_for('arenas'),
                   teams=url_for('teams'),
                   corners=url_for('corners'),
                   state=url_for('state'),
                   matches=url_for('matches'))

@app.route('/arenas')
def arenas():
    comp = g.comp_man.get_comp()

    return jsonify(arenas={name: url_for('get_arena', arena=name)
                            for name in comp.arenas})

@app.route('/arenas/<arena>')
def get_arena(arena):
    return jsonify(name=arena)

def team_info(comp, team):
    scores = comp.scores.league.teams[team.tla]
    return {'name': team.name,
            'get': url_for('get_team', tla=team.tla),
            'tla': team.tla,
            'scores': {'league': scores.league_points,
                       'game': scores.game_points}}


@app.route('/teams')
def teams():
    comp = g.comp_man.get_comp()

    resp = {}
    for team in comp.teams.values():
        resp[team.tla] = team_info(comp, team)

    return jsonify(teams=resp)

@app.route('/teams/<tla>')
def get_team(tla):
    comp = g.comp_man.get_comp()

    team = comp.teams[tla]

    return jsonify(team_info(comp, team))

@app.route("/corners")
def corners():
    comp = g.comp_man.get_comp()
    return jsonify(corners={number: url_for('get_corner', number=number)
                              for number in comp.corners})

@app.route("/corners/<int:number>")
def get_corner(number):
    comp = g.comp_man.get_comp()

    if number not in comp.corners:
        return jsonify(error=True,msg="Invalid corner"), 404

    return jsonify(**comp.corners[number].__dict__)  # **Corner doens't work

@app.route("/state")
def state():
    comp = g.comp_man.get_comp()
    return jsonify(state = comp.state)

@app.route("/matches")
def matches():
    comp = g.comp_man.get_comp()
    matches = []
    for slots in comp.schedule.matches:
        matches.extend(match_json_info(comp, match) for match in slots.values())
    # Filter by type
    if 'type' in request.args:
        matches = [match for match in matches if match['type'] == request.args['type']]
    # Filter by arena
    if 'arena' in request.args:
        matches = [match for match in matches if match['arena'] == request.args['arena']]
    return jsonify(matches=matches)

