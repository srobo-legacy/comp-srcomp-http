import dateutil.parser
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
                   config=url_for('config'),
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

def get_config_dict(comp):
    return {'match_periods': {key: int(value.total_seconds())
                for key, value in comp.schedule.match_period_lengths.items()}}

@app.route("/config")
def config():
    comp = g.comp_man.get_comp()
    return jsonify(config=get_config_dict(comp))

def parse_difference_string(string, type_converter=int):
    """
    Parse a difference string (x..x, ..x, x.., x) and return a function that
    accepts a single argument and returns ``True`` if it is in the difference.
    """
    separator = '..'
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
        ('type', str),
        ('arena', str),
        ('num', int),
        ('start_time', parse_date),
        ('end_time', parse_date)
    ]

    for filter_key, filter_type in filters:
        if filter_key in request.args:
            predicate = parse_difference_string(request.args[filter_key], filter_type)
            matches = [match for match in matches if predicate(filter_type(match[filter_key]))]

    return jsonify(matches=matches)
