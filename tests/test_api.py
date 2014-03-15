
import httplib
import json
import os
import subprocess
import time

PORT = 5555 # deliberately not the default

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_process = None

def setup_module():
    "Module level setup"
    port_file = ROOT + '.test-port'
    if not os.path.exists(port_file):
        global _process
        _process = run_server()
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

def run_server():
    dummy_compstate = ROOT + '/srcomp/tests/dummy/'
    args = [ROOT + '/app.py', dummy_compstate, '-p', str(PORT), '--no-reloader']
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
    assert expected == status

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