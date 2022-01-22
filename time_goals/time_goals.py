from datetime import datetime, timedelta

from sqlalchemy import and_, create_engine, desc, func, select
from sqlalchemy.orm import sessionmaker

from models import Project, TimeEntry, TimeGoal, Plan
from helpers import convert_hours_mins, date_str, time_str, today_str, week_str, week_endpoints

engine = create_engine("sqlite:///test.db", echo=True, future=True)
Session = sessionmaker(bind=engine, future=True)

def parse_view_item(session, item):
    """
    Return a Project or Plan or raise an Exception.
    """
    if item == today_str() or item == "today":
        return Plan.today(session)
    elif item == week_str() or item == "week":
        return Plan.week(session)
    elif type(item) == int:
        # TODO: get the last few days worth of time data in single view
        pass
    elif item == "projects":
        # TODO: get all projects
        pass
    else:
        return (
            Project.get_from_name(session, item) or
            Plan.get_from_name(session, item) or
            None
        )


def parse_date(date):
    """
    Parse relative dates like 5d and 11-12 (Nov, 12th). Dates with
    relative days are interpreted to be in the past unless preceeded
    with a "+":
    - "5d" --> 5 days ago
    - "+5d" --> 5 days in the future

    """
    if date[-1] == "d":
        try:
            relative_days = int(date[0:-1])
            if date[0] == "+":
                date = datetime.today() + timedelta(days=relative_days)
            else:
                date = datetime.today() + timedelta(days=relative_days)
        except ValueError as e:
            print(e)
            print(f"Invalid relative date: <{date}>")
            sys.exit(1)

    else:
        try:
            components = date.split("-")
            if len(components) == 2:
                date = str(datetime.today().year) + "-" + date
            date = datetime.strptime(date, "%Y-%m-%d")
            if date > datetime.today():
                raise Exception("Cannot log time to future date")

        except Exception as e:
            print(f"Invalid relative date: <{date}>")
            print(e)
            sys.exit(1)

    return date_str(date)


def parse_plan_name(plan_name):
    if plan_name == "today":
        plan_name = today_str()
    elif plan_name == "week":
        plan_name = week_str()

    return plan_name


def log_time(session, project_name, minutes, date):
    project_id = Project.get_id(session, project_name)
    TimeEntry.create(session, **{"project_id": project_id,
                                 "minutes": minutes,
                                 "date": date})


# def add_time_goal_to_today(session, project_name: str, minutes: int):
#     Plan.today(session).add_time_goal(session, project_name, minutes)


# def add_time_goal_to_week(session, project_name, minutes, n=0):
#     Plan.week(session, n).add_time_goal(session, project_name, minutes)


def add_time_goal_to_plan(session, project_name, minutes, plan_name):
    if plan_name == today_str():
        Plan.today(session).add_time_goal(session, project_name, minutes)
    elif plan_name == week_str():
        Plan.week(session).add_time_goal(session, project_name, minutes)
    else:
        Plan.get_from_name(session, plan_name).add_time_goal(session, project_name, minutes)




# def interactive_time_entry_delete():
#     while True:
#         ids_to_delete = input("Enter #s to delete separated by spaces: ")
#         if ids_to_delete == "":
#             return
#         try:
#             ids_to_delete = [int(x) - 1 for x in ids_to_delete.split(" ")]
#             ids_to_delete = [time_entries[x].id for x in ids_to_delete]
#             break
#         except Exception as e:
#             print("Enter valid input (empty is valid)")

#     delete_time_entries(ids_to_delete)

def get_plans(session):
    return session.execute(select(Plan)).scalars().all()

def get_projects(session):
    return session.execute(select(Project)).scalars().all()

def get_time_goals(session):
    return session.execute(select(TimeGoal)).scalars().all()

def get_time_entries(session):
    return session.execute(select(TimeEntry)).scalars().all()
