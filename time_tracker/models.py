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

    def __repr__(self):
        return f"<Project({self.name})>"


@mapper_registry.mapped
class TimeEntry:
    __tablename__ = "time_entry"

    id = Column(Integer, primary_key=True)
    project_id = Column(ForeignKey("project.id"), nullable=False)
    minutes = Column(Float)
    date = Column(String)
    created = Column(String, default=datetime.now)

    project = relationship("Project", back_populates="time_entries")

    def __repr__(self):
        return f"<TimeEntry(+{self.minutes}:{self.project}:{self.date})>"


with engine.begin() as conn:
    mapper_registry.metadata.create_all(conn)

################################################################################


# from sqlalchemy import create_engine
# from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
# from sqlalchemy.orm import declarative_base, relationship
# from sqlalchemy.sql import func


# engine = create_engine("sqlite+pysqlite:///testing.db", echo=True, future=True)  # future=True so we use available newer 2.0 features
# Base = declarative_base()


# class Project(Base):
#     __tablename__ = "project"

#     id = Column(Integer, primary_key=True, autoincrement="auto")
#     name = Column(String, unique=True)
#     created_at = Column(DateTime, server_default=func.now())

#     def __init__(self):
#         self.name = name

#     def __repr__(self):
#         return f"<Project: {self.name}>"


# class TimeEntry(Base):
#     __tablename__ = "time_entry"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     project_id = Column(String, ForeignKey("project.id"))
#     date = Column(String)
#     minutes = Column(Float)
#     created_at = Column(DateTime, server_default=func.now())

#     project = relationship("Project")

#     def __init__(self):
#         self.project = project
#         self.date = date
#         self.minutes = minutes

#     def __repr__(self):
#         return


# Base.metadata.create_all(engine)
