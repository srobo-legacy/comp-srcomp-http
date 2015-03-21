#!/usr/bin/env python

"""Update the given compstate repo in a safe manner."""

from subprocess import check_call, check_output

from sr.comp.http.manager import update_lock

DEFAULT_REVISION = 'origin/master'

def add_arguments(parser):
    parser.add_argument("compstate", help = "Competition state git repository path")
    rev_help = "Target revision to update to (default: {})".format(DEFAULT_REVISION)
    parser.add_argument("revision",
                        default = DEFAULT_REVISION,
                        nargs = '?',
                        help = rev_help)

def run_update(args):
    compstate = args.compstate
    revision = args.revision

    # Provide information about where the remotes are
    check_call("git remote -v", shell=True, cwd=args.compstate)

    # Fetch first, don't need to lock for this bit
    check_call("git fetch origin", shell=True, cwd=compstate)

    # Ensure the revision exists (hide successful output)
    check_output(['git', 'rev-parse', revision], cwd=compstate)

    with update_lock(args.compstate):
        check_call(['git', 'checkout', revision], cwd=compstate)

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    args = parser.parse_args()
    run_update(args)

if __name__ == '__main__':
    main()
