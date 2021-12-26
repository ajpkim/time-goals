from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import registry, relationship


mapper_registry = registry()
engine = create_engine("sqlite:///test.db", echo=True, future=True)


@mapper_registry.mapped
class Project:
    __tablename__ = "project"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created = Column(String, default=datetime.now)

    time_entries = relationship("TimeEntry", back_populates="project")
    time_goals = relationship("TimeGoal", back_populates="project")

    def __repr__(self):
        return f"<Project({self.name})>"


@mapper_registry.mapped
class TimeEntry:
    __tablename__ = "time_entry"

    id = Column(Integer, primary_key=True)
    project_id = Column(ForeignKey("project.id"), nullable=False)
    minutes = Column(Integer)
    date = Column(String)
    created = Column(String, default=datetime.now)

    project = relationship("Project", back_populates="time_entries")

    def __repr__(self):
        return f"<TimeEntry(+{self.minutes}:{self.project}:{self.date})>"


@mapper_registry.mapped
class TimeGoal:
    __tablename__ = "time_goal"

    id = Column(Integer, primary_key=True)
    project_id = Column(ForeignKey("project.id"), nullable=False)
    plan_id = Column(ForeignKey("plan.id"), nullable=False)
    minutes = Column(Integer)
    # start_date = Column(String)
    # end_date = Column(String)
    created = Column(String, default=datetime.now)

    project = relationship("Project", back_populates="time_goals")
    plan = relationship("Plan", back_populates="time_goals")

    def __repr__(self):
        return f"<TimeGoal(plan: #{self.plan_id}: project #{self.project_id}: {self.minutes}m:)>"


@mapper_registry.mapped
class Plan:
    __tablename__ = "plan"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    created = Column(String, default=datetime.now)

    time_goals = relationship("TimeGoal", back_populates="plan")

    def __repr__(self):
        return f"<Plan({self.name}: {self.start_date} - {self.end_date})>"


with engine.begin() as conn:
    mapper_registry.metadata.create_all(conn)
