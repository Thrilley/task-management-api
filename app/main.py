from fastapi import FastAPI

from app.api.routes.tasks import router as tasks_router

app = FastAPI(title="Task Management API", version="0.1.0")
app.include_router(tasks_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
