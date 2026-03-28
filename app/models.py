from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Category(str, Enum):
    personal = "personal"
    work = "work"
    shopping = "shopping"
    other = "other"


class TodoCreate(BaseModel):
    text: str
    priority: Priority = Priority.medium
    category: Category = Category.personal
    due_date: Optional[str] = None
    notes: Optional[str] = None


class TodoUpdate(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    category: Optional[Category] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None


class Todo(BaseModel):
    id: str
    user_id: str
    text: str
    completed: bool
    priority: Priority
    category: Category
    due_date: Optional[str]
    notes: Optional[str] = None
    created_by_email: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
