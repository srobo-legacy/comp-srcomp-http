import datetime
import dateutil.parser
import dateutil.tz
from functools import partial
import os.path
from pkg_resources import working_set

from flask import g, Flask, jsonify, request, url_for, abort

from sr.comp.match_period import MatchType
from sr.comp.http.manager import SRCompManager
from sr.comp.http.json import JsonEncoder
from sr.comp.http.query_utils import match_json_info, parse_difference_string


app = Flask('sr.comp.http')
app.json_encoder = JsonEncoder

comp_man = SRCompManager()

@app.before_request
def before_request():
    if "COMPSTATE" in app.config:
        comp_man.root_dir = os.path.realpath(app.config["COMPSTATE"])
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
                   config=url_for('config'),
                   state=url_for('state'),
                   matches=url_for('matches'),
                   periods=url_for('match_periods'),
                   current=url_for('current_state'),
                   knockout=url_for('knockout'))


def format_arena(arena):
    data = {'get': url_for('get_arena', name=arena.name)}
    data.update(arena.__dict__)
    return data


@app.route('/arenas')
def arenas():
    comp = g.comp_man.get_comp()
    return jsonify(arenas={name: format_arena(arena)
                              for name, arena in comp.arenas.items()})


@app.route('/arenas/<name>')
def get_arena(name):
    comp = g.comp_man.get_comp()

    if name not in comp.arenas:
        return jsonify(error=True, msg="Invalid arena"), 404

    return jsonify(**format_arena(comp.arenas[name]))


def team_info(comp, team):
    scores = comp.scores.league.teams[team.tla]
    league_pos = comp.scores.league.positions[team.tla]
    return {'name': team.name,
            'get': url_for('get_team', tla=team.tla),
            'tla': team.tla,
            'league_pos': league_pos,
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

    try:
        team = comp.teams[tla]
    except KeyError:
        abort(404)
    return jsonify(team_info(comp, team))

def format_corner(corner):
    data = {'get': url_for('get_corner', number=corner.number)}
    data.update(corner.__dict__)
    return data

@app.route("/corners")
def corners():
    comp = g.comp_man.get_comp()
    return jsonify(corners={number: format_corner(corner)
                              for number, corner in comp.corners.items()})

@app.route("/corners/<int:number>")
def get_corner(number):
    comp = g.comp_man.get_comp()

    if number not in comp.corners:
        return jsonify(error=True,msg="Invalid corner"), 404

    return jsonify(**format_corner(comp.corners[number]))

@app.route("/state")
def state():
    comp = g.comp_man.get_comp()
    return jsonify(state = comp.state)

def get_config_dict(comp):
    return {'match_slots': {key: int(value.total_seconds())
                for key, value in comp.schedule.match_slot_lengths.items()},
            'server':
              {library: working_set.by_key[library].version
                for library in ('sr.comp',
                                'sr.comp.http',
                                'sr.comp.ranker',
                                'flask')}
            }

@app.route("/config")
def config():
    comp = g.comp_man.get_comp()
    return jsonify(config=get_config_dict(comp))

@app.route("/matches")
def matches():
    comp = g.comp_man.get_comp()
    matches = []
    for slots in comp.schedule.matches:
        matches.extend(match_json_info(comp, match) for match in slots.values())

    def parse_date(string):
        if ' ' in string:
            raise ValueError('Date string should not contain spaces. '
                             "Did you pass in a '+'?")
        return dateutil.parser.parse(string)

    filters = [
        ('type', MatchType, lambda x: x['type']),
        ('arena', str, lambda x: x['arena']),
        ('num', int, lambda x: x['num']),
        ('game_start_time', parse_date, lambda x: x['times']['game']['start']),
        ('game_end_time', parse_date, lambda x: x['times']['game']['end']),
        ('period_start_time', parse_date, lambda x: x['times']['period']['start']),
        ('period_end_time', parse_date, lambda x: x['times']['period']['end'])
    ]

    for filter_key, filter_type, filter_value in filters:
        if filter_key in request.args:
            predicate = parse_difference_string(request.args[filter_key], filter_type)
            matches = [match for match in matches if predicate(filter_type(filter_value(match)))]

    return jsonify(matches=matches)

@app.route("/periods")
def match_periods():
    comp = g.comp_man.get_comp()

    def match_num(period, index):
        #print("bees: ", len(period.matches))
        if not period.matches:
            return None
        games = list(period.matches[index].values())
        return games[0].num

    periods = []
    for match_period in comp.schedule.match_periods:
        data = match_period._asdict()
        data['matches'] = {
            'first_num': match_num(match_period, 0),
            'last_num': match_num(match_period, -1)
        }
        periods.append(data)

    return jsonify(periods=periods)

@app.route("/current")
def current_state():
    comp = g.comp_man.get_comp()

    time = datetime.datetime.now(comp.timezone)
    matches = list(map(partial(match_json_info, comp),
                       comp.schedule.matches_at(time)))

    return jsonify(time=time.isoformat(), matches=matches)


@app.route('/knockout')
def knockout():
    comp = g.comp_man.get_comp()
    return jsonify(rounds=comp.schedule.knockout_rounds)
