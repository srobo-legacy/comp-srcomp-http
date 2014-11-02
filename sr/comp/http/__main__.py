#!/usr/bin/env python

from argparse import ArgumentParser

from sr.comp.http import config, app

parser = ArgumentParser( description = "SR Competition info API HTTP server" )
parser.add_argument("compstate", help = "Competition state git repository path")
parser.add_argument("-p", "--port", type=int, default=5112,
                    help = "Port to listen on")
parser.add_argument("--no-reloader", action="store_false", default=True,
                    dest="reloader", help = "Disable the reloader")
args = parser.parse_args()

config.configure_logging_relative('logging-stdout.ini')

app.config["COMPSTATE"] = args.compstate
app.debug = True
app.run(host='0.0.0.0', port=args.port, use_reloader=args.reloader)
