from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.tasks import router as tasks_router
from app.core.cache import close_cache_connection


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await close_cache_connection()


app = FastAPI(title="Task Management API", version="0.1.0", lifespan=lifespan)
app.include_router(tasks_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
