from datetime import datetime, timedelta

from sqlalchemy import and_, create_engine, desc, func, select
from sqlalchemy.orm import sessionmaker

from models import Project, TimeEntry, TimeGoal, Plan
from helpers import convert_hours_mins, time_str, today_str, week_str, week_endpoints

engine = create_engine("sqlite:///test.db", echo=True, future=True)
Session = sessionmaker(bind=engine, future=True)


def log_time(session, project_name, minutes, date):
    project_id = Project.get_id(session, project_name)
    TimeEntry.create(session, **{"project_id": project_id,
                                 "minutes": minutes,
                                 "date": date})


def add_time_to_today(session, project_name: str, minutes: int):
    Plan.today(session).add_time_goal(session, project_name, minutes)


def add_time_to_week(session, project_name, minutes, n=0):
    Plan.week(session, n).add_time_goal(session, project_name, minutes)


def add_time_to_plan(session, plan_name, project_name, minutes):
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
