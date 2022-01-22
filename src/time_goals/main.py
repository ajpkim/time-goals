import argparse
import datetime
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Plan, Project
from helpers import time_str, today_str, week_str
from time_goals import (
    add_time_goal_to_plan,
    log_time,
    get_projects,
    parse_date,
    parse_plan_name,
    parse_view_item,
)


def main():
    proj_mins_parent_parser = argparse.ArgumentParser(add_help=False)
    proj_mins_parent_parser.add_argument("project", type=str, help="Existing project")
    proj_mins_parent_parser.add_argument("minutes", type=int, help="Time in minutes")

    start_end_parent_parser = argparse.ArgumentParser(add_help=False)
    start_end_parent_parser.add_argument(
        "-s",
        "--start",
        type=str,
        nargs="?",
        const=1,
        default="1900",
        metavar="",
        help="Start date",
    )
    start_end_parent_parser.add_argument(
        "-e",
        "--end",
        type=str,
        nargs="?",
        const=1,
        default=today_str(),
        metavar="",
        help="End date",
    )

    main_parser = argparse.ArgumentParser(prog="Time Goals")
    subparser = main_parser.add_subparsers(dest="command")

    log_parser = subparser.add_parser(
        "log", description="Log time", parents=[proj_mins_parent_parser]
    )
    log_parser.add_argument(
        "date",
        nargs="?",
        const=1,
        type=str,
        help="Date given in relative days ago e.g. '3d', 12-14, or 2021-12-14. Default is today's plan.",
        default=today_str(),
    )

    add_parser = subparser.add_parser(
        "add", description="Add time goal to plan", parents=[proj_mins_parent_parser]
    )
    add_parser.add_argument(
        "plan",
        type=str,
        nargs="?",
        const=1,
        default=today_str(),
        help="Plan to add time goal to. Default is today's plan.",
    )

    view_parser = subparser.add_parser(
        "view",
        description="View time for plan or project. Default is today's plan.",
        parents=[start_end_parent_parser],
    )
    view_parser.add_argument(
        "item",
        type=str,
        nargs="?",
        const=1,
        default=today_str(),
        help="Item to view time for, a Project or Plan. Defaults is today's plan.",
    )

    new_parser = subparser.add_parser(
        "new",
        description="Create new Projects and Plans",
        parents=[start_end_parent_parser],
    )
    new_parser.add_argument(
        "category",
        type=str,
        choices=["project", "plan"],
        help="Create a new Project or Plan.",
    )
    new_parser.add_argument("name", type=str, help="Name of new Project or Plan")

    # start_end_parent_parser(

    # new_parser.add_argument(
    #     "-s", "--start", type=str, metavar="", help="Start date of new Plan"
    # )
    # new_parser.add_argument(
    #     "-e", "--end", type=str, metavar="", help="End date of new Plan"
    # )

    args = main_parser.parse_args()
    engine = create_engine("sqlite:///test.db", echo=False, future=True)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    if args.command == "log":
        try:
            date = parse_date(args.date)
            log_time(session, args.project, args.minutes, date)
        except Exception as e:
            print(f"Invalid time log entry: <{args.project, args.minutes, args.date}>")
            sys.exit(1)

    elif args.command == "add":
        try:
            plan = parse_plan_name(args.plan)
            add_time_goal_to_plan(session, args.project, args.minutes, plan)
        except Exception as e:
            print(e)
            sys.exit(1)

    elif args.command == "view":
        if args.item == "projects":
            report = Project.report(session, start_date=args.start, end_date=args.end)
            print("-------------------------")
            print(f"Project Time Report")
            print(f"{args.start} ... {args.end}")
            print("-------------------------")
            for project, time in sorted(report.items(), key=lambda x: -x[1]):
                print(f"{project:<15} :: {time_str(time)}")
        else:
            try:
                item = parse_view_item(session, args.item)
                if item is None:
                    raise Exception(f"Item <{args.item}> doesn't exist to viewed")
                item.display_status(session)
            except Exception as e:
                print(e)
                sys.exit(1)

    elif args.command == "new":
        print(args)
        if args.category == "project":
            Project.create(session, **{"name": args.name})
        else:
            start_date = parse_date(args.start)
            end_date = parse_date(args.end)
            kwargs = {"name": args.name, "start_date": start_date, "end_date": end_date}
            Plan.create(session, **kwargs)


if __name__ == "__main__":
    main()
