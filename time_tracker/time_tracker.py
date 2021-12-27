from datetime import datetime, timedelta

from sqlalchemy import and_, create_engine, desc, func, select
from sqlalchemy.orm import sessionmaker

from models import Project, TimeEntry, TimeGoal, Plan


engine = create_engine("sqlite:///test.db", echo=True, future=True)
Session = sessionmaker(bind=engine, future=True)


##################################################
## Helpers
def convert_hours_mins(minutes: float) -> (int, int):
    """Convert minutes into hours and minutes"""
    return int(minutes // 60), int(minutes % 60)


def get_time_str(minutes: float) -> str:
    hours, minutes = convert_hours_mins(minutes)
    if hours and minutes:
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"
    elif hours:
        return f"{hours}h"
    elif minutes:
        return f"{minutes}m"
    else:
        return ""


def get_or_create(session, model, **kwargs):
    """
    TODO: Throw error if multiple instances meet criteria
    """
    instance = session.execute(select(model).filter_by(**kwargs)).scalar()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def get_today_plan(session):
    today_str = datetime.today().strftime("%Y-%m-%d")
    kwargs = {"name": today_str, "start_date": today_str, "end_date": today_str}
    return get_or_create(session, Plan, **kwargs)


##################################################
## Get model object info
def get_plan_id(session, name: str):
    return session.execute(select(Plan).filter_by(name=name)).scalar().id


def get_project_id(session, name: str):
    return session.execute(select(Project).filter_by(name=name)).scalar().id


# def get_time_goal(time_goal_id: int):
#     return get_model_object(TimeGoal, "id", time_goal_id)


# def get_time_entry(time_entry_id: int):
#     return get_model_object(TimeEntry, "id", time_entry_id)


# def get_model_object(model, filter_field, identifier):
#     with Session.begin() as session:
#         return session.execute(
#             select(model).filter_by(filter_field=identifier)
#         ).scalar()

##################################################
## Create
def create_project(session, name: str):
    project = Project(name=name)
    session.add(project)
    session.commit()
    return project


def create_time_entry(session, project_name: str, minutes: float, date: str):
    stmt = select(Project).filter_by(name=project_name)
    project = session.execute(stmt).scalar()
    time_entry = TimeEntry(project_id=project.id, minutes=minutes, date=date)
    session.add(time_entry)
    session.commit()
    return time_entry


def create_time_goal(session, project_name: str, plan_name: str, minutes: int):
    project_id = get_project_id(session, project_name)
    plan_id = get_plan_id(session, plan_name)
    time_goal = TimeGoal(project_id=project_id, plan_id=plan_id, minutes=minutes)
    session.add(time_goal)
    session.commit()
    return time_goal


def create_plan(session, name: str, start_date: str, end_date: str):
    plan = Plan(name=name, start_date=start_date, end_date=end_date)
    session.add(plan)
    session.commit()
    return plan


##################################################
## Get status
def get_plan_status(session, plan_name: str) -> {str: (int, int)}:
    plan = session.execute(select(Plan).filter_by(name=plan_name)).scalar()
    stmt = (
        select(Project.name, func.sum(TimeEntry.minutes), TimeGoal.minutes)
        .join(TimeEntry)
        .where(and_(TimeEntry.date >= plan.start_date, TimeEntry.date <= plan.end_date))
        .group_by(Project.name)
        .join(TimeGoal)
    )
    return {proj: (mins, goal) for proj, mins, goal in session.execute(stmt)}


def get_project_status(session, project_name: str) -> {str: int}:
    project = session.execute(select(Project).filter_by(name=project_name)).scalar()
    today = datetime.today()
    timeframes = {
        "All Time": datetime(1, 1, 1),
        "Year": today.replace(month=1, day=1),
        "Month": today.replace(day=1),
        "Week": today - timedelta(days=today.weekday()),
        "Today": today,
    }
    time_entries = project.time_entries
    for timeframe, date in timeframes.items():
        date = date.strftime("%Y-%m-%d")
        time_entries = [x for x in time_entries if x.date >= date]
        timeframes[timeframe] = sum([x.minutes for x in time_entries])

    return timeframes


def get_today_status(session) -> {str: [int]}:
    """Get information about time tracked/alloated for today."""
    today = datetime.today().strftime("%Y-%m-%d")
    stmt = (
        select(Project.name, func.sum(TimeEntry.minutes))
        .join(TimeEntry)
        .where(TimeEntry.date == today)
        .group_by(Project.name)
        .order_by(desc(func.sum(TimeEntry.minutes)))
    )
    projects_minutes = session.execute(stmt)
    projects_minutes_goals = {proj: [mins, 0] for (proj, mins) in projects_minutes}
    today_plan = get_today_plan(session)
    for goal in today_plan.time_goals:
        project = session.execute(
            select(Project).filter_by(id=goal.project_id)
        ).scalar()
        if project.name in projects_minutes_goals:
            projects_minutes_goals[project.name][1] = goal.minutes
        else:
            projects_minutes_goals[project.name] = [0, goal.minutes]

    return projects_minutes_goals


##################################################
## Update Plan
def update_plan(plan_name, project_name, minutes):
    """Assign a new time goal for given project in given plan"""
    pass


##################################################
## Other stuff
def create_today_plan(session):
    today_str = datetime.today().strftime("%Y-%m-%d")
    plan = create_plan(today_str, today_str, today_str, session)
    session.add(plan)
    session.commit()
    return plan


def create_week_plan(session, relative_start_date: int):
    """
    TODO
    - Create a plan with ISO week # as name unless specified
    """
    # week_num = datetime.today().isocalendar().week
    week_num = datetime.now().strftime("%W")

    pass


def allocate_time_today(session, project_name: str, minutes: int):
    today_plan = get_today_plan(session)
    project_id = get_project_id(session, project_name)
    plan_project_ids = [x.project_id for x in today_plan.time_goals]

    if project_id in plan_project_ids:
        time_goal = session.execute(
            select(TimeGoal).where(
                and_(
                    TimeGoal.project_id == project_id, TimeGoal.plan_id == today_plan.id
                )
            )
        ).scalar()
        time_goal.minutes += minutes
        session.commit()
    else:
        time_goal = create_time_goal(session, project_name, today_plan.name, minutes)


def update_time_goal():
    pass


def get_recent_time_entries(session, n: int):
    stmt = select(TimeEntry).order_by(desc(TimeEntry.created)).limit(10)
    n_recent_time_entries = session.execute(stmt).scalars().all()

    # interactive_update_recent_time_entries(n_recent_time_entries)


def interactive_update_recent_time_entries(time_entries: [TimeEntry]):
    report = f"--- Last {len(time_entries)} Time Entries ---\n"
    for i, time_entry in enumerate(time_entries, 1):
        time_str = get_time_str(time_entry.minutes)
        report += f"{i:<5}+{time_str} {time_entry.project.name} ({time_entry.date})\n"
    print(report)

    while True:
        ids_to_delete = input("Enter #s to delete separated by spaces: ")
        if ids_to_delete == "":
            break
        try:
            ids_to_delete = [int(x) - 1 for x in ids_to_delete.split(" ")]
            ids_to_delete = [time_entries[x].id for x in ids_to_delete]
            break
        except Exception as e:
            print("Enter valid input (empty is valid)")

    delete_time_entries(ids_to_delete)


def delete_time_entries(session, ids: [int]):
    for x in ids:
        session.delete(session.get(TimeEntry, x))
    session.commit()


def add_time_goal_to_plan(session, plan_name, project_name, minutes):
    plan = get_plan(plan_name)
