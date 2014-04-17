
import datetime
import httplib
import json
import os
import shutil
import subprocess
import tempfile
import time
import yaml

PORT = 5555 # deliberately not the default

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_process = None
_temp_dir = None

def setup_module():
    "Module level setup"
    port_file = ROOT + '.test-port'
    if not os.path.exists(port_file):
        global _process
        dummy_compstate = create_compstate(ROOT + '/srcomp/tests/dummy/')
        print "Using '{0}'.".format(dummy_compstate)
        _process = run_server(dummy_compstate)
        line = _process.stdout.readline()
        retcode = _process.poll()
        assert retcode is None, _process.stdout.read()
        assert line.startswith(" * Running on"), line + '\n' + _process.stdout.read()
    else:
        PORT = int(open(port_file).read())

def teardown_module():
    "Module level teardown"
    if _process is not None:
        _process.terminate()
        _process.wait()
    shutil.rmtree(_temp_dir)

def create_compstate(original):
    global _temp_dir
    _temp_dir = tempfile.mkdtemp(prefix='compstate-')
    tmp_compstate = os.path.join(_temp_dir, 'compstate')
    shutil.copytree(original, tmp_compstate)
    make_matches_today(tmp_compstate)
    return tmp_compstate

def make_matches_today(root):
    schedule_path = os.path.join(root, "schedule.yaml")
    s = None
    with open(schedule_path, 'r') as f:
        s = yaml.load(f)
    first = s['match_periods']['league'][0]
    now = datetime.datetime.now()
    first['start_time'] = now - datetime.timedelta(minutes=1)
    end = now + datetime.timedelta(days=1)
    first['end_time'] = end
    del first['max_end_time']

    with open(schedule_path, 'w') as f:
        f.write(yaml.dump(s))

def run_server(compstate_path):
    args = [ROOT + '/app.py', compstate_path, '-p', str(PORT), '--no-reloader']
    proc = subprocess.Popen(args,
                            stderr=subprocess.STDOUT,
                            stdout=subprocess.PIPE)
    return proc

def make_connection():
    return httplib.HTTPConnection("127.0.0.1", PORT)

def server_get(endpoint):
    conn = make_connection()

    conn.request("GET", endpoint)

    resp = conn.getresponse()
    data = resp.read()
    return resp, data

def assert_json(endpoint, expected):
    resp, raw_data = server_get(endpoint)
    status = resp.status
    assert expected == status, raw_data

    data = json.loads(raw_data)
    assert data is not None

    return data

def test_endpoints():
    endpoints = [
        '/matches/A/0',
        '/matches/A/1',
        '/matches/B/0',
        '/matches/B/1',

        '/matches/A/0-1',
        '/matches/B/0-1',

        '/matches/A/current',
        '/matches/B/current',

        '/scores/league',
        '/arenas',
        '/corner/0',
        '/corner/1',
        '/corner/2',
        '/corner/3',
    ]

    for e in endpoints:
        yield assert_json, e, 200
