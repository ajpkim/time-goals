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
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"


##################################################
## Get model object info
def get_plan_id(name: str):
    with Session.begin() as session:
        return session.execute(select(Plan).filter_by(name=name)).scalar().id


def get_project_id(name: str):
    with Session.begin() as session:
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
def create_project(name: str):
    with Session.begin() as session:
        project = Project(name=name)
        session.add(project)
        session.commit()
        return project


def create_time_entry(project_name: str, minutes: float, date: str):
    with Session.begin() as session:
        stmt = select(Project).filter_by(name=project_name)
        project = session.execute(stmt).scalar()
        time_entry = TimeEntry(project_id=project.id, minutes=minutes, date=date)
        session.add(time_entry)
        session.commit()
        return time_entry


def create_time_goal(project_name: str, plan_name: str, minutes: int):
    with Session.begin() as session:
        project_id = get_project_id(project_name)
        plan_id = get_plan_id(plan_name)
        time_goal = TimeGoal(project_id=project_id, plan_id=plan_id, minutes=minutes)
        session.add(time_goal)
        session.commit()
        # return time_goal


def create_plan(name: str, start_date: str, end_date: str):
    with Session.begin() as session:
        plan = Plan(name=name, start_date=start_date, end_date=end_date)
        session.add(plan)
        session.commit()
        # return plan


##################################################
## Get status
def get_plan_status(plan_name: str) -> {str: (int, int)}:
    with Session.begin() as session:
        plan = session.execute(select(Plan).filter_by(name=plan_name)).scalar()
        stmt = (
            select(Project.name, func.sum(TimeEntry.minutes), TimeGoal.minutes)
            .join(TimeEntry)
            .where(
                and_(TimeEntry.date >= plan.start_date, TimeEntry.date <= plan.end_date)
            )
            .group_by(Project.name)
            .join(TimeGoal)
        )
        return {proj: (mins, goal) for proj, mins, goal in session.execute(stmt)}


def get_project_status(project_name: str) -> {str: int}:
    with Session.begin() as session:
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


def get_today_status() -> {str: [int]}:
    """
    Get plan agnostic today information.
    """
    today = datetime.today().strftime("%Y-%m-%d")
    with Session.begin() as session:
        stmt = (
            select(Project.name, func.sum(TimeEntry.minutes))
            .join(TimeEntry)
            .where(TimeEntry.date == today)
            .group_by(Project.name)
            .order_by(desc(func.sum(TimeEntry.minutes)))
        )
        projects_minutes = session.execute(stmt)
        projects_minutes_goals = {project: [minutes, 0] for (project, minutes) in projects_minutes}

        try:
            today_plan = session.execute(select(Plan).filter_by(name=today)).one()
        except Exception as e:
            today_plan = create_today_plan()

        for goal in today_plan.time_goals:
            project = session.execute(select(Project).filter_by(id=goal.project_id)).scalar()
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
def create_today_plan():
    today_str = datetime.today().strftime("%Y-%m-%d")
    with Session.begin() as session:
        plan = create_plan(today_str, today_str, today_str)
        session.add(plan)
        session.commit(plan)
        return plan


def create_week_plan(relative_start_date: int):
    """
    TODO
    - Create a plan with ISO week # as name unless specified
    """
    # week_num = datetime.today().isocalendar().week
    week_num = datetime.now().strftime("%W")
    with Session.begin() as session:
        pass


def allocate_time_today(project_name: str, minutes: int):
    today_str = datetime.today().strftime("%Y-%m-%d")
    with Session.begin() as session:

        today_plan = create_plan(today_str, today_str, today_str)
        session.add(today_plan)
        session.commit()

        # today_plan = session.execute(select(Plan).filter_by(name=today_str)).scalar()
        # if not today_plan:
        #     print('\n\n\n\nCREATING PLAN\n\n\n\n')
        #     today_plan = create_today_plan()
        ## Causes db issues "OperationalError"...
        # try:
        #     today_plan = session.execute(select(Plan).filter_by(name=today_str)).one()
        # except Exception as e:
        #     today_plan = create_today_plan()

        time_goal = create_time_goal(project_name, today_plan.name, minutes)
        session.add(time_goal)
        session.commit()


def update_time_goal():
    pass


def get_recent_time_entries(n: int):
    with Session.begin() as session:
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


def delete_time_entries(ids: [int]):
    with Session.begin() as session:
        for x in ids:
            session.delete(session.get(TimeEntry, x))
        session.commit()


def add_time_goal_to_plan(plan_name, project_name, minutes):
    with Session.begin() as session:
        plan = get_plan(plan_name)
