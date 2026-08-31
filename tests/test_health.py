from fastapi.testclient import TestClient

from app.main import app
from app.models.task import TaskStatus
from app.schemas.task import TaskUpdate


def test_healthcheck() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_task_update_keeps_only_supplied_fields() -> None:
    payload = TaskUpdate(status=TaskStatus.done)
    assert payload.model_dump(exclude_unset=True) == {"status": TaskStatus.done}
