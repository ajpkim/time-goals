from datetime import datetime, timedelta

from sqlalchemy import create_engine, desc, func, select
from sqlalchemy.orm import sessionmaker

from models import Project, TimeEntry, TimeGoal


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
## Create
def create_project(name: str):
    with Session.begin() as session:
        project = Project(name=name)
        session.add(project)
        session.commit()


def create_time_entry(project_name: str, minutes: float, date: str):
    with Session.begin() as session:
        stmt = select(Project).filter_by(name=project_name)
        project = session.execute(stmt).scalar()
        time_entry = TimeEntry(project_id=project.id, minutes=minutes, date=date)
        session.add(time_entry)
        session.commit()


def create_time_goal(project_name: str, minutes: int, start_date: str, end_date: str):
    with Session.begin() as session:
        project_id = session.execute(
            select(Project.id).filter_by(name=project_name)
        ).scalar()
        time_goal = TimeGoal(project_id=project_id,
                             minutes=minutes,
                             start_date=start_date,
                             end_date=end_date)
        session.add(time_goal)
        session.commit()

##################################################
## Other stuff
def get_recent_time_entries(n: int):
    with Session.begin() as session:
        stmt = select(TimeEntry).order_by(desc(TimeEntry.created)).limit(10)
        n_recent_time_entries = session.execute(stmt).scalars().all()

        interactive_update_recent_time_entries(n_recent_time_entries)


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

def get_timeframe_status(start_date, end_date ):
    """
    TODO: Gather all the info for the given time frame: projects, time entries, time goals
    """
    pass

def view_project(project_name: str):
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
        time_entries = (
            project.time_entries
        )  # Exists because of defined table relationships in models.py
        for key, date in timeframes.items():
            date = date.strftime("%Y-%m-%d")
            time_entries = [x for x in time_entries if x.date >= date]
            minutes = sum([x.minutes for x in time_entries])
            timeframes[key] = minutes

        print_project_report(project.name, timeframes.keys(), timeframes.values())

"""
This should be changed to "get_today_status()" which should gather all the
info for the day: projects, time entries, and time goals

This same pattern for arb date ranges
"""
def view_today():
    today = datetime.today().strftime("%Y-%m-%d")
    with Session.begin() as session:
        stmt = (
            select(Project.name, func.sum(TimeEntry.minutes))
            .join(TimeEntry)
            .where(TimeEntry.date == today)
            .group_by(Project.name)
            .order_by(desc(func.sum(TimeEntry.minutes)))
        )
        projects_times = session.execute(stmt)
        projects, minutes = zip(*projects_times)

        print_today_report(projects, minutes)

##################################################
## Printers
def print_today_report(projects: [str], minutes: [float]):
    total_time = 0
    print("\n--- Today's Tracked Time ---")
    report = ""
    for project, mins in zip(projects, minutes):
        total_time += mins
        time_str = get_time_str(mins)
        report += f"{project:<25} {time_str}\n"

    total_time = get_time_str(total_time)
    report += ".....\n" + "Total Time".ljust(25) + f"{total_time}\n"
    print(report)


def print_project_report(project_name: str, timeframes: [str], minutes: [float]):
    print(f"\n---------- {project_name} ----------")
    report = ""
    for timeframe, mins in zip(timeframes, minutes):
        time_str = get_time_str(mins)
        report = f"{timeframe:<25} {time_str}\n" + report

    print(report)
