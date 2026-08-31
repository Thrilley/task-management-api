from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db)) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("", response_model=list[TaskRead])
async def list_tasks(db: AsyncSession = Depends(get_db)) -> list[Task]:
    return list((await db.scalars(select(Task).order_by(Task.created_at.desc()))).all())


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)) -> Task:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
