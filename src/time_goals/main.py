import argparse, sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Plan, Project
from helpers import today_str, week_str
from time_goals import log_time, add_time_to_today, add_time_to_week

def main():
    parser = argparse.ArgumentParser(prog="Time Tracker")
    subparser = parser.add_subparsers(dest="command")

    log_parser = subparser.add_parser("log")
    log_parser.add_argument("project", type=str)
    log_parser.add_argument("minutes", type=int)

    today_parser = subparser.add_parser("today")
    today_parser.add_argument("project", type=str)
    today_parser.add_argument("minutes", type=int)

    week_parser = subparser.add_parser("week")
    week_parser.add_argument("project", type=str)
    week_parser.add_argument("minutes", type=int)

    view_parser = subparser.add_parser("view")
    view_parser.add_argument("name", type=str)
    view_parser.add_argument("-m", "--model", type=str)

    # TODO: have separate command for planning in advance e.g. week +1
    args = parser.parse_args()
    engine = create_engine("sqlite:///test.db", echo=True, future=True)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    if args.command == "log":
        # TODO: add options for logging time to past days
        try:
            log_time(session, args.project, args.minutes, today_str())
        except Exception as e:
            print(f"{args.project} is not a Project")
            sys.exit(1)

    if args.command == "today":
        try:
            add_time_to_today(session, args.project, args.minutes)
        except Exception as e:
            print("Invalid command")
            sys.exit(1)

    if args.command == "week":
        try:
            add_time_to_week(session, args.project, args.minutes)
        except Exception as e:
            print("Invalid command")
            sys.exit(1)

    if args.command == "view":

        if args.name == "today":
            Plan.today(session).display_status(session)

        elif args.name == "week":
            Plan.week(session).display_status(session)

        elif args.model == "project":
            try:
                Project.get_from_name(session, name=args.name).display_status(session)
            except Exception as e:
                print("Invalid command")
                sys.exit(1)

        elif args.model == "plan":
            try:
                Plan.get_from_name(session, name=args.name).display_status(session)
            except Exception as e:
                print("Invalid command")
                sys.exit(1)


if __name__ == "__main__":
    main()
