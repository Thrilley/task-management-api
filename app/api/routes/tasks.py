from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_task_list, invalidate_task_list_cache, set_task_list
from app.db.session import get_db
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db)) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    await invalidate_task_list_cache()
    return task


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    status: TaskStatus | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[Task]:
    cache_key = f"tasks:list:{status.value if status else 'all'}:{limit}:{offset}"
    cached_tasks = await get_task_list(cache_key)
    if cached_tasks is not None:
        return [TaskRead.model_validate(task) for task in cached_tasks]

    query = select(Task).order_by(Task.created_at.desc()).limit(limit).offset(offset)
    if status is not None:
        query = query.where(Task.status == status)
    tasks = list((await db.scalars(query)).all())
    cache_payload = [TaskRead.model_validate(task).model_dump(mode="json") for task in tasks]
    await set_task_list(cache_key, cache_payload)
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)) -> Task:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int, payload: TaskUpdate, db: AsyncSession = Depends(get_db)
) -> Task:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    await invalidate_task_list_cache()
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)) -> None:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
    await invalidate_task_list_cache()
