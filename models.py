from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

# Junction Table for Many-to-Many relationship
project_members_association = Table(
    'project_project_members_user',
    Base.metadata,
    Column('projectId', Integer, ForeignKey('project.id'), primary_key=True),
    Column('userBadge', Integer, ForeignKey('user.badge'), primary_key=True)
)

class User(Base):
    __tablename__ = "user"
    badge = Column(Integer, primary_key=True, autoincrement=False)
    firstName = Column(String(255))
    lastName = Column(String(255))
    email = Column(String(255))
    projects = relationship("Project", secondary=project_members_association, back_populates="members")

class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(125))
    status = Column(String(50))
    client = Column(String(125))
    # description stores the JSON string containing your table data
    description = Column(Text) 
    repositories = Column(Text)
    members = relationship("User", secondary=project_members_association, back_populates="projects")