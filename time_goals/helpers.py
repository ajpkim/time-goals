from datetime import datetime, timedelta

from sqlalchemy import select


def convert_hours_mins(minutes: int) -> (int, int):
    """Convert minutes into hours and minutes"""
    return int(minutes // 60), int(minutes % 60)


def time_str(minutes: int) -> str:
    hours, minutes = convert_hours_mins(minutes)
    if hours and minutes:
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"
    elif hours:
        return f"{hours}h"
    elif minutes:
        return f"{minutes}m"
    else:
        return ""


def date_str(date):
    return date.strftime("%Y-%m-%d")


def today_str():
    return datetime.today().strftime("%Y-%m-%d")


def week_str(n=0):
    date = datetime.today() + timedelta(weeks=n)
    return date.strftime("%Y-W%W")


def week_endpoints(date: datetime) -> (str, str):
    start = date - timedelta(weeks=date.weekday())
    end = date + timedelta(days=(6 - date.weekday()))
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def parse_date(date):
    """
    Parse relative dates like 5d and 11-12 (Nov, 12th). Dates with
    relative days are interpreted to be in the past unless preceeded
    with a "+" (a consequence of argparse not able to handle arg vals with "-" prefix):
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
