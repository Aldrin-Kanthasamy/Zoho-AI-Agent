from enum import Enum
from pydantic import BaseModel
from typing import Optional


class UserRole(str, Enum):
    superadmin = "superadmin"
    developer = "developer"
    support = "support"


class TaskStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"


class UserCreate(BaseModel):
    name: str
    email: str
    role: UserRole
    skills: Optional[str] = ""
    is_available: bool = True


class TaskCreate(BaseModel):
    external_id: Optional[str] = None
    title: str
    description: Optional[str] = ""
    skill_needed: str
    priority: Optional[str] = "Medium"


class TicketCreate(BaseModel):
    external_id: Optional[str] = None
    subject: str
    description: Optional[str] = ""
    skill_needed: str
    priority: Optional[str] = "Medium"


class NLCommand(BaseModel):
    text: str
