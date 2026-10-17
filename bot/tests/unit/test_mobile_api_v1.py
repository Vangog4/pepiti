from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.testclient import TestClient

from app.api.mobile_auth import decode_jwt, issue_jwt
from app.api.v1.app import create_fastapi_app
from app.api.v1.dependencies import get_current_user, get_db_session, get_redis
from app.core.config import settings
from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.user import UserModel


@pytest.fixture
def mock_user():
    user = MagicMock(spec=UserModel)
    user.id = 42
    user.telegram_id = 123456789
    user.first_name = "Анна"
    user.last_name = "Иванова"
    user.username = "anna_test"
    user.language_code = "ru"
    user.timezone = "Europe/Moscow"
    user.reminder_time = "09:00"
    user.is_premium = True
    user.subscription_expires_at = datetime(2027, 1, 1, 0, 0, 0, tzinfo=UTC)
    user.training_days = 7
    user.created_at = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    return user


@pytest.fixture
def mock_pet():
    pet = MagicMock(spec=PetModel)
    pet.id = 101
    pet.user_id = 42
    pet.name = "Бобик"
    pet.breed = "Корги"
    pet.sex = "male"
    pet.age_category = "Молодой (1–3 года)"
    pet.age_months = 18
    pet.size_category = "medium"
    pet.weight_kg = 12.5
    pet.training_level = "2"
    pet.temperament = "Энергичный"
    pet.behavior_issues = None
    pet.goal = "Базовое послушание"
    pet.energy_level = "high"
    pet.health_notes = None
    pet.training_days = 7
    pet.created_at = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    pet.updated_at = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    return pet


@pytest.fixture
def mock_redis():
    r = AsyncMock()
    store: dict[str, str] = {}

    async def get_val(key):
        return store.get(key)

    async def set_val(key, val, ex=None):
        store[key] = str(val)
        return True

    async def del_val(key):
        return store.pop(key, None) is not None

    r.get = AsyncMock(side_effect=get_val)
    r.set = AsyncMock(side_effect=set_val)
    r.delete = AsyncMock(side_effect=del_val)
    return r


@pytest.fixture
def mock_db_session(mock_user, mock_pet):
    session = AsyncMock()

    class MockResult:
        def __init__(self, data):
            self._data = data

        def scalar_one_or_none(self):
            return self._data[0] if self._data else None

        def scalars(self):
            class ScalarCollection:
                def __init__(self, items):
                    self._items = items

                def all(self):
                    return self._items

                def first(self):
                    return self._items[0] if self._items else None

            return ScalarCollection(self._data)

        def all(self):
            return self._data

        def fetchall(self):
            return self._data

    async def execute_mock(stmt):
        stmt_str = str(stmt).lower()
        if "from users" in stmt_str:
            return MockResult([mock_user])
        if "from pets" in stmt_str:
            return MockResult([mock_pet])
        if "from training_plans" in stmt_str:
            return MockResult([])
        if "from coach_threads" in stmt_str:
            return MockResult([])
        return MockResult([])

    session.execute = AsyncMock(side_effect=execute_mock)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def client(mock_db_session, mock_redis, mock_user):
    app = create_fastapi_app()

    async def override_get_db_session():
        yield mock_db_session

    async def override_get_redis():
        return mock_redis

    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(app)


def test_openapi_schema_and_docs():
    app = create_fastapi_app()
    client = TestClient(app)
    res = client.get("/openapi.json")
    assert res.status_code == 200
    data = res.json()
    assert data["info"]["title"] == "Pepito Mobile API"
    paths = data["paths"]

    # Critical sync & auth routes
    assert "/api/v1/auth/guest" in paths
    assert "/api/v1/auth/telegram/session" in paths
    assert "/api/v1/auth/telegram/check" in paths
    assert "/api/v1/auth/telegram/code" in paths
    assert "/api/v1/auth/vk" in paths
    assert "/api/v1/auth/link" in paths
    assert "/api/v1/sync/pull" in paths
    assert "/api/v1/sync/push" in paths
    assert "/api/v1/profile" in paths
    assert "/api/v1/pets" in paths
    assert "/api/v1/training/plan" in paths
    assert "/api/v1/coach/threads" in paths
    assert "/api/v1/subscription/status" in paths


def test_jwt_issue_and_decode_validity():
    secret = "test_mobile_secret_123"
    token = issue_jwt(user_id=123, secret=secret, expire_days=7)
    assert isinstance(token, str)

    decoded_uid = decode_jwt(token, secret)
    assert decoded_uid == 123

    # Wrong secret
    assert decode_jwt(token, "wrong_secret") is None


def test_auth_guest_flow(client, mock_redis):
    res = client.post(
        "/api/v1/auth/guest",
        json={"device_id": "test-device-uuid-123", "device_name": "iPhone 15", "platform": "ios"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_id"] > 0
    assert data["expires_in_days"] == settings.MOBILE_JWT_EXPIRE_DAYS


def test_telegram_session_creation(client):
    res = client.post("/api/v1/auth/telegram/session")
    assert res.status_code == 200
    data = res.json()
    assert "session_token" in data
    assert "deep_link" in data
    assert "t.me" in data["deep_link"]
    assert "auth_" in data["deep_link"]


@pytest.mark.asyncio
async def test_telegram_code_auth(client, mock_redis):
    # Seed connect code
    await mock_redis.set("tg_connect_code:654321", "42")

    res = client.post("/api/v1/auth/telegram/code", json={"code": "654321"})
    assert res.status_code == 200
    data = res.json()
    assert data["user_id"] == 42
    assert "access_token" in data


def test_profile_endpoints(client, mock_user):
    res = client.get("/api/v1/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 42
    assert data["first_name"] == "Анна"
    assert data["is_premium"] is True
    assert data["training_days"] == 7

    # Update profile
    patch_res = client.patch(
        "/api/v1/profile",
        json={"first_name": "Анна Обновленная", "timezone": "UTC+3", "reminder_time": "10:30"},
    )
    assert patch_res.status_code == 200
    pdata = patch_res.json()
    assert pdata["first_name"] == "Анна Обновленная"


def test_pets_list_endpoint(client, mock_pet):
    res = client.get("/api/v1/pets")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Бобик"
    assert data[0]["breed"] == "Корги"


def test_subscription_status_endpoint(client, mock_user):
    res = client.get("/api/v1/subscription/status")
    assert res.status_code == 200
    data = res.json()
    assert data["is_premium"] is True
    assert data["tier"] == "premium"
    assert len(data["plans"]) >= 3


def test_subscription_plans_endpoint(client):
    res = client.get("/api/v1/subscription/plans")
    assert res.status_code == 200
    plans = res.json()
    assert isinstance(plans, list)
    assert any(p["plan_id"] == "premium_1m" for p in plans)


def test_sync_pull_full_snapshot(client, mock_user, mock_pet):
    res = client.get("/api/v1/sync/pull")
    assert res.status_code == 200
    data = res.json()
    assert "server_time" in data
    assert data["profile"]["id"] == 42
    assert len(data["pets"]) >= 1
    assert data["active_pet_id"] == 101
    assert "subscription" in data
    assert data["subscription"]["is_premium"] is True


def test_sync_push_offline_batch(client, mock_user):
    payload = {
        "client_timestamp": datetime.now(tz=UTC).isoformat(),
        "task_changes": [],
        "profile_update": {"reminder_time": "11:00"},
        "pet_update": None,
    }
    res = client.post("/api/v1/sync/push", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["profile_updated"] is True
    assert "current_state" in data
    assert data["current_state"]["profile"]["reminder_time"] == "11:00"


def test_health_check_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["app"] == "pepito-mobile-api"


def test_export_training_pdf_signature_and_headers(client, mock_pet, mock_db_session):
    plan = MagicMock()
    plan.id = 200
    plan.pet_id = mock_pet.id
    plan.title = "План на неделю"
    plan.goal = "Послушание"
    plan.tasks = []

    # Update execute mock to return pet and plan
    orig_execute = mock_db_session.execute

    async def custom_execute(stmt):
        s = str(stmt).lower()
        if "from training_plans" in s:
            mock_res = MagicMock()
            mock_res.scalar_one_or_none.return_value = plan
            mock_res.scalars.return_value.all.return_value = [plan]
            mock_res.scalars.return_value.first.return_value = plan
            return mock_res
        return await orig_execute(stmt)

    mock_db_session.execute = AsyncMock(side_effect=custom_execute)

    res = client.get(f"/api/v1/training/pdf?pet_id={mock_pet.id}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert "filename=" in res.headers["content-disposition"]
    assert res.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_telegram_session_single_use(client, mock_redis):
    # Seed session
    session_data = {"status": "authenticated", "user_id": 42}
    await mock_redis.set("tg_session:test_token_123", json.dumps(session_data))

    # First check returns authenticated
    res1 = client.get("/api/v1/auth/telegram/check?session_token=test_token_123")
    assert res1.status_code == 200
    assert res1.json()["status"] == "authenticated"
    assert res1.json()["token_data"]["user_id"] == 42

    # Second check must return expired because key was deleted
    res2 = client.get("/api/v1/auth/telegram/check?session_token=test_token_123")
    assert res2.status_code == 200
    assert res2.json()["status"] == "expired"
    assert res2.json()["token_data"] is None


def test_subscription_status_lifetime_premium(client, mock_user):
    mock_user.is_premium = True
    mock_user.subscription_expires_at = None

    res = client.get("/api/v1/subscription/status")
    assert res.status_code == 200
    data = res.json()
    assert data["is_premium"] is True
    assert data["tier"] == "premium"
    assert data["days_left"] == 9999


def test_push_registration_clean_redis(client, mock_redis):
    res = client.post(
        "/api/v1/push/register",
        json={"push_token": "apns_device_token_xyz", "platform": "ios", "device_id": "dev_123"},
    )
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert res.json()["platform"] == "ios"


def test_pet_deletion_cascade(client, mock_pet, mock_db_session):
    res = client.delete(f"/api/v1/pets/{mock_pet.id}")
    assert res.status_code == 204
    assert mock_db_session.delete.called
    assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_account_linking_transfers_and_returns_token(client, mock_redis):
    await mock_redis.set("tg_connect_code:888999", "99")

    res = client.post(
        "/api/v1/auth/link",
        json={"provider": "telegram_code", "credential": "888999", "device_id": "my_iphone_123"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["merged_user_id"] == 99
    assert data["token_data"]["user_id"] == 99
    assert "access_token" in data["token_data"]
