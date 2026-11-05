import pytest

from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestRegisterAPIView:
    def test_successful_api_registration(self, client):
        response = client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "s3cretpass",
            },
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["bio"] == ""
        assert "id" in data

    def test_api_registration_conflict(self, client):
        UserFactory(email="taken@example.com")

        response = client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "taken@example.com",
                "password": "s3cretpass",
            },
            content_type="application/json",
        )

        assert response.status_code == 409
        assert response.json()["error"] == "Email already registered"

    def test_api_registration_validation_error(self, client):
        response = client.post(
            "/api/auth/register/",
            {"username": "ab", "email": "not-an-email", "password": "short"},
            content_type="application/json",
        )

        assert response.status_code == 400
        assert "username" in response.json()
        assert "email" in response.json()
        assert "password" in response.json()

    def test_username_format_validation(self, client):
        response = client.post(
            "/api/auth/register/",
            {
                "username": "user name!",
                "email": "new@example.com",
                "password": "s3cretpass",
            },
            content_type="application/json",
        )

        assert response.status_code == 400
        assert (
            response.json()["username"][0]
            == "Username must contain only letters and numbers"
        )


class TestLoginAPIView:
    def test_successful_api_login(self, client):
        UserFactory(username="alice")

        response = client.post(
            "/api/auth/login/",
            {"username": "alice", "password": "s3cretpass"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "alice"
        assert data["access"]
        assert data["refresh"]

    def test_failed_api_login(self, client):
        UserFactory(username="alice")

        response = client.post(
            "/api/auth/login/",
            {"username": "alice", "password": "wrongpass"},
            content_type="application/json",
        )

        assert response.status_code == 401
        assert response.json()["error"] == "Invalid credentials"


class TestTokenRefreshView:
    def test_successful_token_refresh(self, client):
        UserFactory(username="alice")
        login = client.post(
            "/api/auth/login/",
            {"username": "alice", "password": "s3cretpass"},
            content_type="application/json",
        )
        refresh = login.json()["refresh"]

        response = client.post(
            "/api/auth/token/refresh/",
            {"refresh": refresh},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["access"]

    def test_invalid_refresh_token_rejected(self, client):
        response = client.post(
            "/api/auth/token/refresh/",
            {"refresh": "not-a-valid-token"},
            content_type="application/json",
        )

        assert response.status_code == 401
        assert "access" not in response.json()
