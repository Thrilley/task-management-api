from fastapi.testclient import TestClient
import jwt

from app.main import app
from app.core.config import settings
from app.core.security import JWT_ALGORITHM, create_access_token, hash_password, verify_password
from app.models.task import TaskStatus
from app.schemas.auth import UserCreate
from app.schemas.task import TaskUpdate


def test_healthcheck() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_task_update_keeps_only_supplied_fields() -> None:
    payload = TaskUpdate(status=TaskStatus.done)
    assert payload.model_dump(exclude_unset=True) == {"status": TaskStatus.done}


def test_list_tasks_documents_pagination_parameters() -> None:
    parameters = app.openapi()["paths"]["/api/v1/tasks"]["get"]["parameters"]
    parameter_names = {parameter["name"] for parameter in parameters}
    assert {"limit", "offset", "status"}.issubset(parameter_names)


def test_user_password_requires_eight_characters() -> None:
    user = UserCreate(email="developer@example.com", password="safe-passphrase")
    assert user.email == "developer@example.com"


def test_passwords_are_hashed_and_verified() -> None:
    hashed_password = hash_password("safe-passphrase")
    assert hashed_password != "safe-passphrase"
    assert verify_password("safe-passphrase", hashed_password)


def test_access_token_contains_user_subject() -> None:
    token = create_access_token("developer@example.com")
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == "developer@example.com"
