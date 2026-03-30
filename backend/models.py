from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum


class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    developer = "developer"
    support = "support"


class TaskStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.developer)
    skills = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tasks = relationship("Task", back_populates="assignee")
    tickets = relationship("Ticket", back_populates="assignee")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    skill_needed = Column(String, nullable=False)
    priority = Column(String, default="Medium")
    status = Column(Enum(TaskStatus), default=TaskStatus.open)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assignee = relationship("User", back_populates="tasks")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, nullable=True)
    subject = Column(String, nullable=False)
    description = Column(String, nullable=True)
    skill_needed = Column(String, nullable=False)
    priority = Column(String, default="Medium")
    status = Column(Enum(TicketStatus), default=TicketStatus.open)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assignee = relationship("User", back_populates="tickets")
