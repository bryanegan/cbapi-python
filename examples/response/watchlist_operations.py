#!/usr/bin/env python
#

import sys
from cbapi.response.models import Watchlist
from cbapi.example_helpers import build_cli_parser, get_cb_response_object
from cbapi.errors import ServerError
import logging

log = logging.getLogger(__name__)


def list_watchlists(cb, parser, args):
    for w in cb.select(Watchlist):
        print(w)
        print("")


def add_watchlist(cb, parser, args):
    w = cb.create(Watchlist, data={"name": args.name, "index_type": args.type})
    w.query = args.query

    log.debug("Adding watchlist: {0:s}".format(str(w)))

    try:
        w.save()
    except ServerError as se:
        print("Could not add watchlist: {0:s}".format(str(se)))
    except Exception as e:
        print("Could not add watchlist: {0:s}".format(str(e)))
    else:
        log.debug("Watchlist data: {0:s}".format(str(w)))
        print("Added watchlist. New watchlist ID is {0:s}".format(w.id))


def delete_watchlist(cb, parser, args):
    try:
        if args.id:
            attempted_to_find = "ID of {0:s}".format(args.id)
            watchlists = [cb.select(Watchlist, args.id, force_init=True)]
        else:
            attempted_to_find = "name {0:s}".format(args.name)
            watchlists = cb.select(Watchlist).where("name:{0:s}".format(args.name))[::]
            if not len(watchlists):
                raise Exception("No watchlists match")
    except Exception as e:
        print("Could not find watchlist with {0:s}: {1:s}".format(attempted_to_find, str(e)))
        return

    num_matching_watchlists = len(watchlists)
    if num_matching_watchlists > 1 and not args.force:
        print("{0:d} watchlists match {1:s} and --force not specified. No action taken.".format(num_matching_watchlists,
                                                                                           attempted_to_find))
        return

    for f in watchlists:
        try:
            f.delete()
        except Exception as e:
            print("Could not delete watchlist with {0:s}: {1:s}".format(attempted_to_find, str(e)))
        else:
            print("Deleted watchlist id {0:s} with name {1:s}".format(f.id, f.name))


def main():
    parser = build_cli_parser()
    commands = parser.add_subparsers(help="Watchlist commands", dest="command_name")

    list_command = commands.add_parser("list", help="List all configured watchlists")

    add_command = commands.add_parser("add", help="Add new watchlist")
    add_command.add_argument("-N", "--name", help="Name of watchlist", required=True)
    add_command.add_argument("-q", "--query", help="Watchlist query string, e.g. process_name:notepad.exe",
                             required=True)
    add_command.add_argument("-t", "--type", help="Watchlist type 'events' or 'modules'", required=True)

    del_command = commands.add_parser("delete", help="Delete watchlists")
    del_watchlist_specifier = del_command.add_mutually_exclusive_group(required=True)
    del_watchlist_specifier.add_argument("-i", "--id", type=int, help="ID of watchlist to delete")
    del_watchlist_specifier.add_argument("-N", "--name", help="Name of watchlist to delete. Specify --force to delete"
                                         " multiple watchlists that have the same name")
    del_command.add_argument("--force", help="If NAME matches multiple watchlists, delete all matching watchlists",
                             action="store_true", default=False)

    args = parser.parse_args()
    cb = get_cb_response_object(args)

    if args.command_name == "list":
        return list_watchlists(cb, parser, args)
    elif args.command_name == "add":
        return add_watchlist(cb, parser, args)
    elif args.command_name == "delete":
        return delete_watchlist(cb, parser, args)


if __name__ == "__main__":
    sys.exit(main())
