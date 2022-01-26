import argparse

from helpers import today_str

def add_project_mins_pos_args(parser):
    parser.add_argument("project", type=str, help="Existing project")
    parser.add_argument("minutes", type=int, help="Time in minutes")


def add_start_end_opt_args(parser):
    parser.add_argument(
        "-s",
        "--start",
        type=str,
        nargs="?",
        const=1,
        default="1900",
        metavar="",
        help="Start date",
    )
    parser.add_argument(
        "-e",
        "--end",
        type=str,
        nargs="?",
        const=1,
        default=today_str(),
        metavar="",
        help="End date",
    )


def attach_log_subparser(subparser) -> None:
    log_subparser = subparser.add_parser("log", help="Log time to Projects.")
    add_project_mins_pos_args(log_subparser)
    log_subparser.add_argument(
        "date",
        nargs="?",
        const=1,
        type=str,
        help="Date given in relative days ago e.g. '3d', 12-14, or 2021-12-14. Default is today's plan.",
        default=today_str(),
    )


def attach_view_subparser(subparser):
    view_subparser = subparser.add_parser("view", help="View data.")
    view_subparser.add_argument(
        "item",
        type=str,
        nargs="?",
        const=1,
        default=today_str(),
        help="Item to view time for, a Project or Plan. Defaults is today's plan.",
    )

def attach_add_subparser(subparser):
    add_subparser = subparser.add_parser("add", help="Add time to a Plan.")
    add_project_mins_pos_args(add_subparser)
    add_subparser.add_argument(
        "plan",
        type=str,
        nargs="?",
        const=1,
        default=today_str(),
        help="Plan to add time goal to. Default is today's plan.",
    )


def attach_new_subparser(subparser):
    new_subparser = subparser.add_parser("new", help="Create new Projects and Plans")

def get_parser():
    parser = argparse.ArgumentParser(description="Tool for planning, tracking, and analyzing time.")
    subparser = parser.add_subparsers(dest="command", metavar="")
    attach_log_subparser(subparser)
    attach_view_subparser(subparser)
    attach_add_subparser(subparser)
    attach_new_subparser(subparser)
    return parser
