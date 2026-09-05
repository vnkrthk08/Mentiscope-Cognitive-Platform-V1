import pytest
import uuid
from httpx import AsyncClient
from app.infrastructure.identity.password_hasher import PasswordHasher
from app.infrastructure.identity.jwt_service import JWTService
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.identity.entities.user import User
from app.infrastructure.identity.token_store import token_store


@pytest.fixture(autouse=True)
async def clean_lockouts_and_database():
    """Autouse fixture ensuring IP and account lockouts are fully reset between test cases."""
    # Reset both local host and mock IP addresses
    await token_store.reset_failed_logins("127.0.0.1")
    await token_store.reset_failed_logins("0.0.0.0")
    yield
    await token_store.reset_failed_logins("127.0.0.1")
    await token_store.reset_failed_logins("0.0.0.0")


@pytest.mark.asyncio
async def test_password_hashing():
    plain = "SuperPassword123"
    hashed = PasswordHasher.hash_password(plain)
    assert hashed != plain
    assert PasswordHasher.verify_password(plain, hashed) is True
    assert PasswordHasher.verify_password("wrongpassword", hashed) is False


@pytest.mark.asyncio
async def test_jwt_generation_and_decoding():
    user_id = "test-user-id"
    role = "Candidate"
    perms = ["assessment:view", "report:view"]
    session_id = "session-id"

    token = JWTService.create_access_token(user_id, role, perms, session_id)
    assert token is not None

    payload = JWTService.decode_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert payload["permissions"] == perms
    assert payload["session_id"] == session_id


@pytest.mark.asyncio
async def test_user_registration_and_login_flow(async_client: AsyncClient):
    # 1. Register candidate account
    reg_payload = {
        "username": "candidate_test",
        "email": "cand_test@mentiscope.com",
        "password": "SecretPassword123",
    }
    reg_res = await async_client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["username"] == "candidate_test"
    assert reg_data["email"] == "cand_test@mentiscope.com"
    assert "Candidate" in reg_data["roles"]

    # 2. Login to retrieve access/refresh tokens
    login_payload = {
        "username": "candidate_test",
        "password": "SecretPassword123",
    }
    login_res = await async_client.post("/api/v1/auth/login", data=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data

    # 3. Access current profile GET /users/me
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = await async_client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["username"] == "candidate_test"
    assert "assessment:view" in me_data["permissions"]

    # 4. Refresh token rotation (with JTI unique claims)
    ref_payload = {"refresh_token": token_data["refresh_token"]}
    ref_res = await async_client.post("/api/v1/auth/refresh", json=ref_payload)
    assert ref_res.status_code == 200
    new_token_data = ref_res.json()
    assert new_token_data["access_token"] != token_data["access_token"]

    # 5. Access profile update
    update_payload = {"username": "candidate_updated"}
    update_res = await async_client.put(
        "/api/v1/users/me", json=update_payload, headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["username"] == "candidate_updated"


@pytest.mark.asyncio
async def test_role_based_access_control(async_client: AsyncClient):
    # Register an admin account manually in DB to test permissions
    async with UnitOfWork() as uow:
        admin_role = await uow.roles.get_by_name("Administrator")
        hashed = PasswordHasher.hash_password("AdminPass123!")
        admin_user = User(
            user_id=str(uuid.uuid4()),
            username="admin_user_test",
            email="admin_test@mentiscope.com",
            hashed_password=hashed,
            is_active=True,
            is_verified=True,
            roles=[admin_role],
        )
        await uow.users.save(admin_user)

        # Register a candidate manually in DB to avoid sequence dependencies
        cand_role = await uow.roles.get_by_name("Candidate")
        hashed_cand = PasswordHasher.hash_password("SecretPassword123")
        cand_user = User(
            user_id=str(uuid.uuid4()),
            username="cand_user_test",
            email="cand_user_test@mentiscope.com",
            hashed_password=hashed_cand,
            is_active=True,
            is_verified=True,
            roles=[cand_role],
        )
        await uow.users.save(cand_user)
        await uow.commit()

    # Login as Candidate
    login_payload = {
        "username": "cand_user_test",
        "password": "SecretPassword123",
    }
    login_cand_res = await async_client.post("/api/v1/auth/login", data=login_payload)
    assert login_cand_res.status_code == 200
    cand_tokens = login_cand_res.json()
    cand_headers = {"Authorization": f"Bearer {cand_tokens['access_token']}"}

    # Attempt to list roles as Candidate (should return 403 Forbidden)
    roles_cand_res = await async_client.get("/api/v1/roles", headers=cand_headers)
    assert roles_cand_res.status_code == 403

    # Login as Administrator
    login_admin_payload = {
        "username": "admin_user_test",
        "password": "AdminPass123!",
    }
    login_admin_res = await async_client.post("/api/v1/auth/login", data=login_admin_payload)
    assert login_admin_res.status_code == 200
    admin_tokens = login_admin_res.json()
    admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}

    # Attempt to list roles as Administrator (should succeed 200)
    roles_admin_res = await async_client.get("/api/v1/roles", headers=admin_headers)
    assert roles_admin_res.status_code == 200
    assert len(roles_admin_res.json()) >= 1


@pytest.mark.asyncio
async def test_brute_force_lockout_rate_limit(async_client: AsyncClient):
    # Execute consecutive failed logins using incorrect passwords on an isolated user
    bad_login_payload = {
        "username": "non_existent_user_test",
        "password": "wrongpassword123",
    }

    # 5 attempts are allowed
    for _ in range(5):
        res = await async_client.post("/api/v1/auth/login", data=bad_login_payload)
        assert res.status_code == 401

    # 6th attempt should trigger account lock 429 Too Many Requests
    lock_res = await async_client.post("/api/v1/auth/login", data=bad_login_payload)
    assert lock_res.status_code == 429
    data = lock_res.json()
    msg = data.get("message") or data.get("detail", "")
    assert "locked" in msg
