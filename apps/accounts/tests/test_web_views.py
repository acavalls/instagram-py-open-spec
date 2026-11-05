import pytest

from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestRegisterView:
    def test_successful_registration(self, client):
        response = client.post(
            "/web/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "s3cretpass",
            },
        )

        assert response.status_code == 302
        assert response.url == "/web/login/"

    def test_duplicate_email_rejected(self, client):
        UserFactory(email="taken@example.com")

        response = client.post(
            "/web/register/",
            {
                "username": "newuser",
                "email": "taken@example.com",
                "password": "s3cretpass",
            },
        )

        assert response.status_code == 200
        assert b"Email already registered" in response.content

    def test_duplicate_username_rejected(self, client):
        UserFactory(username="takenuser")

        response = client.post(
            "/web/register/",
            {
                "username": "takenuser",
                "email": "new@example.com",
                "password": "s3cretpass",
            },
        )

        assert response.status_code == 200
        assert b"Username already taken" in response.content

    def test_password_too_short_rejected(self, client):
        response = client.post(
            "/web/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "short",
            },
        )

        assert response.status_code == 200
        assert b"Password must be at least 8 characters" in response.content

    def test_username_format_validation(self, client):
        too_short = client.post(
            "/web/register/",
            {
                "username": "ab",
                "email": "new@example.com",
                "password": "s3cretpass",
            },
        )
        non_alnum = client.post(
            "/web/register/",
            {
                "username": "user name!",
                "email": "new@example.com",
                "password": "s3cretpass",
            },
        )
        too_long = client.post(
            "/web/register/",
            {
                "username": "a" * 151,
                "email": "new@example.com",
                "password": "s3cretpass",
            },
        )

        assert too_short.status_code == 200
        assert b"Username must be between 3 and 150 characters" in too_short.content
        assert non_alnum.status_code == 200
        assert b"Username must contain only letters and numbers" in non_alnum.content
        assert too_long.status_code == 200
        assert b"Username must be between 3 and 150 characters" in too_long.content


class TestLoginView:
    def test_successful_web_login(self, client):
        UserFactory(username="alice")

        response = client.post(
            "/web/login/", {"username": "alice", "password": "s3cretpass"}
        )

        assert response.status_code == 302
        assert response.url == "/web/"

    def test_failed_web_login_hides_the_cause(self, client):
        UserFactory(username="alice")

        wrong_password = client.post(
            "/web/login/", {"username": "alice", "password": "wrongpass"}
        )
        unknown_user = client.post(
            "/web/login/", {"username": "nobody", "password": "whatever1"}
        )

        assert wrong_password.status_code == 200
        assert unknown_user.status_code == 200
        assert b"Invalid credentials" in wrong_password.content
        assert b"Invalid credentials" in unknown_user.content


class TestLogoutView:
    def test_successful_logout(self, client):
        client.force_login(UserFactory(username="alice"))

        response = client.post("/web/logout/")

        assert response.status_code == 302
        assert response.url == "/web/login/"

    def test_protected_pages_require_login(self, client):
        response = client.get("/web/")

        assert response.status_code == 302
        assert response.url.startswith("/web/login/")


class TestAuthTemplates:
    def test_login_template_renders_expected_fields(self, client):
        response = client.get("/web/login/")

        assert response.status_code == 200
        content = response.content
        assert b'name="username"' in content
        assert b'name="password"' in content
        assert b'action="/web/login/"' in content

    def test_register_template_renders_expected_fields(self, client):
        response = client.get("/web/register/")

        assert response.status_code == 200
        content = response.content
        assert b'name="email"' in content
        assert b'name="username"' in content
        assert b'name="password"' in content
        assert b'action="/web/register/"' in content
