from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class TaskUpdate(BaseModel):
    """Fields are optional so PATCH can update only the supplied values."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None


class TaskRead(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
