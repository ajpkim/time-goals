from typing import List

from rich.table import Table
from rich.console import Console

import helpers
from models import Plan, Project, TimeEntry


def add_time(session, project: str, mins: int, plan: str) -> None:
    """TODO"""
    try:
        plan = helpers.parse_plan_name(plan)
        Plan.get_from_name(session, plan).add_time_goal(session, project, mins)
    except Exception as e:
        print(e)
        print("Cannot add time to given Project and Plan")


def log(session, project, minutes, date) -> None:
    """TODO"""
    try:
        project_id = Project.get_id(session, project)
        TimeEntry.create(
            session, **{"project_id": project_id, "minutes": minutes, "date": date}
        )
    except AttributeError as e:
        print(f"Project: <{project}> doesn't exist")


def new(session, category, name, start=None, end=None) -> None:
    """TODO"""
    if category == "project":
        Project.create(session, **{"name": name})
    elif category == "plan":
        Plan.create(session, **{"name": name, "start_date": start, "end_date": end})


def get_view_data(session, item):
    """
    Return a Project or Plan or raise an Exception.
    """
    if item == "today":
        item = helpers.today_str()
    elif item == "week":
        item = helpers.week_str()

    item = (
        Project.get_from_name(session, item) or Plan.get_from_name(session, item) or None
    )

    return item.data(session) if item else None


def datum_to_str(x):
    if type(x) == str:
        return x
    elif type(x) == int:
        return helpers.time_str(x)
    else:
        return str(x)


def print_table(data) -> None:
    """Print nice tables from namedtuples data using rich.table objects."""
    title = type(data[0]).__name__
    title = title.replace("_", " ")
    table = Table(title=title)
    for col in data[0]._fields:
        table.add_column(col)
    for row in data:
        row = map(datum_to_str, row)
        table.add_row(*row)
    Console().print(table)


def view(session, item) -> None:
    """TODO"""
    data = get_view_data(session, item)
    if data:
        # df = pd.DataFrame.from_records(data, columns=data[0]._fields)
        # print(df)
        # for row in data:
        #     print(row)
        print_table(data)
    else:
        print(f"No data to view for <{item}>")
