import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from time_goals import add_time, log, new, view

from parsers import get_parser
from models import Plan, Project


def main(session, args):
    if args.command == "add":
        add_time(session, plan=args.plan)
    elif args.command == "log":
        log(session, project=args.project, minutes=args.mins, date=args.date)
    elif args.command == "new":
        new(session, category=args.category, name=args.name)
    elif args.command == "view":
        view(session, item=args.item)


if __name__ == "__main__":

    engine = create_engine("sqlite:///test.db", echo=False, future=True)
    Session = sessionmaker(bind=engine, future=True)
    session = Session()
    args = get_parser().parse_args()
    main(session, args)