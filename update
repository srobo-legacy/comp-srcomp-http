#!/usr/bin/env python

"""Update the given compstate repo in a safe manner."""

from sr.comp.raw_compstate import RawCompstate

from sr.comp.http.manager import update_lock

DEFAULT_REVISION = 'origin/master'
BOLD = '\033[1m'
FAIL = '\033[91m'
ENDC = '\033[0m'

def add_arguments(parser):
    parser.add_argument("compstate", help = "Competition state git repository path")
    rev_help = "Target revision to update to (default: {})".format(DEFAULT_REVISION)
    parser.add_argument("revision",
                        default = DEFAULT_REVISION,
                        nargs = '?',
                        help = rev_help)

def run_update(args):
    compstate = RawCompstate(args.compstate, local_only=True)
    revision = args.revision

    # Provide information about where the remotes are
    compstate.show_remotes()

    # Fetch first, don't need to lock for this bit
    compstate.fetch()

    # Ensure the revision exists
    if not compstate.has_commit(revision):
        msg = "Cannot update to unknown revision '{0}'".format(revision)
        exit(BOLD + FAIL + msg + ENDC)

    with update_lock(args.compstate):
        compstate.checkout(revision)

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    args = parser.parse_args()
    run_update(args)

if __name__ == '__main__':
    main()
