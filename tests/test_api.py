from __future__ import print_function

import datetime
from dateutil.tz import tzlocal
from six.moves import http_client as httplib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import yaml

PORT = 5555 # deliberately not the default

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(ROOT, 'srcomp'))
from sr.comp import yaml_loader

_process = None
_temp_dir = None

def setup_module():
    "Module level setup"
    port_file = ROOT + '.test-port'
    if not os.path.exists(port_file):
        global _process
        dummy_compstate = create_compstate(ROOT + '/tests/dummy/')
        print("Using '{0}'.".format(dummy_compstate))
        _process = run_server(dummy_compstate)
        line = _process.stdout.readline()
        assert line.startswith("logging configured"), line
        line = _process.stdout.readline()
        assert line.startswith(" * Running on"), line
        retcode = _process.poll()
        assert retcode is None, line + '\n' + _process.stdout.read()
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
    fix_gitdir(tmp_compstate, original)
    return tmp_compstate

def make_matches_today(root):
    schedule_path = os.path.join(root, "schedule.yaml")
    s = yaml_loader.load(schedule_path)
    first = s['match_periods']['league'][0]
    now = datetime.datetime.now(tzlocal())
    first['start_time'] = now - datetime.timedelta(minutes=1)
    end = now + datetime.timedelta(days=1)
    first['end_time'] = end
    del first['max_end_time']

    with open(schedule_path, 'w') as f:
        f.write(yaml.dump(s))

def fix_gitdir(target, reference):
    PREFIX = "gitdir:"
    target_git = os.path.join(target, '.git')

    if os.path.isdir(target_git):
        # nothing to do, will have been copied just fine
        return

    relative_gitdir = None
    with open(target_git, 'r') as fd:
        content = fd.read()
        relative_gitdir = content[len(PREFIX):]
        relative_gitdir = relative_gitdir.strip()

    gitdir = os.path.join(reference, relative_gitdir)
    gitdir = os.path.abspath(gitdir)

    with open(target_git, 'w') as fd:
        print(PREFIX, gitdir, file=fd)

def run_server(compstate_path):
    args = [sys.executable, '-m', 'sr.comp.http',
            compstate_path, '-p', str(PORT), '--no-reloader']
    proc = subprocess.Popen(args,
                            stderr=subprocess.STDOUT,
                            stdout=subprocess.PIPE,
                            universal_newlines=True)
    time.sleep(1)  # to wait for the server to become alive
    return proc

def make_connection():
    return httplib.HTTPConnection("127.0.0.1", PORT)

def server_get(endpoint):
    conn = make_connection()

    conn.request("GET", endpoint)

    resp = conn.getresponse()
    data = resp.read().decode('utf-8')
    return resp, data

def assert_json(endpoint, expected, expected_data=None):
    resp, raw_data = server_get(endpoint)
    status = resp.status
    assert expected == status, raw_data

    data = json.loads(raw_data)
    if expected_data is None:
        assert data is not None
    else:
        assert data == expected_data, str(data)

    return data

def test_endpoints():
    endpoints = [
        '/',
        '/arenas',
        '/arenas/A',
        '/arenas/B',
        '/teams',
        '/teams/CLF',
        '/corners',
        '/corners/0',
        '/corners/1',
        '/corners/2',
        '/corners/3',
        '/matches',
        '/matches?arenas=A&range=current',
        '/matches?arenas=B&range=current',
        '/matches?range=0-1',
        '/matches?arenas=B&range=1',
        '/matches?type=knockout',
        '/state'
    ]

    for e in endpoints:
        yield assert_json, e, 200

def test_root():
    assert_json('/', 200, {'config': '/config',
                           'arenas': '/arenas',
                           'teams': '/teams',
                           'corners': '/corners',
                           'matches': '/matches',
                           'state': '/state'})

