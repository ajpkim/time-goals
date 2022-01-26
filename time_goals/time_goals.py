from models import TimeEntry, Plan, Project

import helpers


def add_time(session, project: str, mins: int, plan: str) -> None:
    """TODO"""
    plan = helpers.parse_plan_name(plan)
    Plan.get_from_name(session, plan).add_time_goal(session, project, mins)


def log(session, project, mins, date) -> None:
    """TODO"""
    project_id = Project.get_id(session, project_name)
    TimeEntry.create(
        session, **{"project_id": project_id, "minutes": minutes, "date": date}
    )


def new(session, category, name, start=None, end=None) -> None:
    """TODO"""
    if category == "project":
        Project.create(session, **{"name": name})
    elif category == "plan":
        Plan.create(session, **{"name": name, "start_date": start, "end_date": end})


def get_view_item(session, item):
    """
    Return a Project or Plan or raise an Exception.
    """
    if item == helpers.today_str() or item == "today":
        return Plan.today(session)
    elif item == helpers.week_str() or item == "week":
        return Plan.week(session)
    elif type(item) == int:
        # TODO: get the last few days worth of time data in single view
        pass
    elif item == "projects":
        # TODO: get all projects
        pass
    else:
        return (
            Project.get_from_name(session, item)
            or Plan.get_from_name(session, item)
            or None
        )


def view(session, item) -> None:
    """TODO"""
    item = get_view_item(session, item)
    if item is not None:
        item.display_status(session)
