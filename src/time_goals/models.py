from datetime import datetime, timedelta

from sqlalchemy import and_, create_engine, desc, func, select
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import registry, relationship

from helpers import time_str, today_str, week_str, week_endpoints

mapper_registry = registry()
engine = create_engine("sqlite:///test.db", echo=True, future=True)


class Base:

    id = Column(Integer, primary_key=True)

    @classmethod
    def create(cls, session, **kwargs):
        instance = cls(**kwargs)
        session.add(instance)
        session.commit()
        return instance

    @classmethod
    def get_or_create(cls, session, **kwargs):
        instance = session.execute(select(cls).filter_by(**kwargs)).scalar()
        if instance:
            return instance
        else:
            return cls.create(session, **kwargs)

    @classmethod
    def get_from_id(cls, session, id):
        return session.execute(select(cls).filter_by(id=id)).scalar()

    @classmethod
    def get_from_name(cls, session, name):
        return session.execute(select(cls).filter_by(name=name)).scalar()

    @classmethod
    def recent(cls, session, n=5):
        recent = session.execute(select(cls).order_by(desc(cls.created)).limit(n))
        return recent.scalars().all()


@mapper_registry.mapped
class Project(Base):
    __tablename__ = "project"

    name = Column(String, nullable=False)
    created = Column(String, default=datetime.now)
    time_entries = relationship("TimeEntry", back_populates="project")
    time_goals = relationship("TimeGoal", back_populates="project")

    @classmethod
    def get_id(cls, session, name):
        return session.execute(select(Project).filter_by(name=name)).scalar().id

    @classmethod
    def get_name(cls, session, id):
        return cls.get_from_id(session, id).name

    @classmethod
    def report(cls, session, names=[], start_date="1900", end_date=today_str()):
        print(names, start_date, end_date)
        if not names:
            projects = session.execute(select(Project)).scalars().all()
        else:
            try:
                projects = [
                    Project.get_from_name(session, project).name for project in names
                ]
            except Exception as e:
                print(e)
        data = {proj.name: proj.get_time(session, start_date, end_date) for proj in projects}
        return
        return data

    # @classmethod
    # def display_report(cls, session, names, start_date, end_date):
    #     # report = cls.report()

    #     data = {proj.name: proj.get_time(session, start_date, end_date) for proj in projects}

    #     # else:
    #     #     try:

    #     #         data = {proj.name: proj.get_time(session, start_date, end_date) for proj in
    #     #         # data = {        #
    #     #         data = {}
    #     #         for project in names:
    #     #             proj = Project.get_from_name(session, project)
    #     #             data[project] = proj
    #         # except Exception as e:
    #         #     print(e)
    #     return data

    def get_time(self, session, start="1900-01-01", end=today_str()):
        """
        TODO
        """
        return sum(
            session.execute(
                select(TimeEntry.minutes).where(
                    and_(
                        TimeEntry.project_id == self.id,
                        TimeEntry.date >= start,
                        TimeEntry.date <= end,
                    )
                )
            )
            .scalars()
            .all()
        )

    def status(self, session) -> {str: int}:
        today = datetime.today()
        status = {
            "All Time": datetime(1, 1, 1),
            "Year": today.replace(month=1, day=1),
            "Month": today.replace(day=1),
            "Week": today - timedelta(days=today.weekday()),
            "Today": today,
        }
        time_entries = self.time_entries
        for timeframe, date in status.items():
            date = date.strftime("%Y-%m-%d")
            time_entries = [x for x in time_entries if x.date >= date]
            status[timeframe] = sum([x.minutes for x in time_entries])

        return status

    def status_report(self, session):
        status = self.status(session)
        report = f"--- {self.name} Project Time ---\n"
        for timeframe, minutes in list(status.items())[::-1]:
            minutes = time_str(minutes)
            report += f"{timeframe:<15} {minutes}\n"
        report += "--------------------------"
        return report

    def display_status(self, session):
        print(self.status_report(session))

    def __repr__(self):
        return f"<Project({self.name})>"


@mapper_registry.mapped
class TimeEntry(Base):
    __tablename__ = "time_entry"

    project_id = Column(ForeignKey("project.id"), nullable=False)
    minutes = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    created = Column(String, default=datetime.now)
    project = relationship("Project", back_populates="time_entries")

    def __repr__(self):
        return f"<TimeEntry(+{self.minutes}:{self.project}:{self.date})>"


@mapper_registry.mapped
class TimeGoal(Base):
    __tablename__ = "time_goal"

    project_id = Column(ForeignKey("project.id"), nullable=False)
    plan_id = Column(ForeignKey("plan.id"), nullable=False)
    minutes = Column(Integer, nullable=False)
    created = Column(String, default=datetime.now)
    project = relationship("Project", back_populates="time_goals")
    plan = relationship("Plan", back_populates="time_goals")

    def update_minutes(self, session, minutes):
        if self.minutes + minutes <= 0:
            session.delete(self)
        else:
            self.minutes += minutes
        session.commit()

    def __repr__(self):
        return f"<TimeGoal(plan: #{self.plan_id}: project #{self.project_id}: {self.minutes}m:)>"


@mapper_registry.mapped
class Plan(Base):
    __tablename__ = "plan"

    name = Column(String)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    created = Column(String, default=datetime.now)
    time_goals = relationship("TimeGoal", back_populates="plan")

    @classmethod
    def today(cls, session):
        today = today_str()
        kwargs = {"name": today, "start_date": today, "end_date": today}
        return cls.get_or_create(session, **kwargs)

    @classmethod
    def week(cls, session, n=0):
        week = week_str(n)
        date = datetime.today() + timedelta(weeks=n)
        week_start, week_end = week_endpoints(date)
        kwargs = {"name": week, "start_date": week_start, "end_date": week_end}
        return cls.get_or_create(session, **kwargs)

    def projects(self, session):
        return [
            Project.get_from_id(session, goal.project_id) for goal in self.time_goals
        ]

    def add_time_goal(self, session, project_name: str, minutes: int):
        project_id = Project.get_id(session, project_name)
        if project_id in [project.id for project in self.projects(session)]:
            time_goal = session.execute(
                select(TimeGoal).where(
                    and_(TimeGoal.project_id == project_id, TimeGoal.plan_id == self.id)
                )
            ).scalar()
            time_goal.update_minutes(session, minutes)
        else:
            kwargs = {
                "project_id": project_id,
                "plan_id": self.id,
                "minutes": minutes,
            }
            TimeGoal.create(session, **kwargs)

    def time_entries(self, session) -> [TimeEntry]:
        time_entries = session.execute(
            select(TimeEntry).where(
                and_(TimeEntry.date >= self.start_date, TimeEntry.date <= self.end_date)
            )
        )
        return time_entries.scalars().all()

    def status(self, session) -> {str: [int, int]}:
        status = {}
        for entry in self.time_entries(session):
            project = Project.get_name(session, entry.project_id)
            status[project] = [entry.minutes, 0]

        for goal in self.time_goals:
            project = Project.get_name(session, goal.project_id)
            if project in status:
                status[project][1] = goal.minutes
            else:
                status[project] = [0, goal.minutes]

        return status

    def status_report(self, session):
        status = self.status(session)
        total_time = 0
        total_time_goal = 0
        report = f"\n---------- {self.name} Status ----------\n"
        report += "Projects                   Time  :: Goal\n"

        for project, (mins, goal) in status.items():
            total_time += mins
            total_time_goal += goal
            mins, goal = time_str(mins), time_str(goal)
            report += f"{project:<25} {mins:<6} :: {goal}\n"

        total_time = time_str(total_time)
        total_time_goal = time_str(total_time_goal)

        report += ".....\n"
        report += "Total Time".ljust(26) + f"{total_time:<6} :: {total_time_goal}\n"
        report += "------------------------------------------"
        return report

    def display_status(self, session):
        print(self.status_report(session))

    def __repr__(self):
        return f"<Plan({self.name}: {self.start_date} - {self.end_date})>"


with engine.begin() as conn:
    mapper_registry.metadata.create_all(conn)
