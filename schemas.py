from pydantic import BaseModel, EmailStr, field_validator, constr
from typing import Optional, Annotated
from datetime import date

class UserCreate(BaseModel):
    username: Annotated[str, constr(min_length=3, max_length=30)]
    email: EmailStr

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: date
    status: str = "pending"

    @field_validator('due_date')
    @classmethod
    def due_not_before_today(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("Due date cannot be in the past")
        return v

    @field_validator('status')
    @classmethod
    def valid_status(cls, v: str) -> str:
        allowed = {"pending", "in_progress", "completed"}  # ← made consistent
        if v not in allowed:
            raise ValueError(f"Status must be one of: {allowed}")
        return v

class TaskCreate(TaskBase):
    user_id: int   # renamed for clarity

class Task(TaskBase):
    id: int
    user_id: int