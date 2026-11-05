import pytest

from apps.accounts.services.user_service import UserService
from apps.accounts.tests.factories import UserFactory
from apps.accounts.use_cases import (
    AuthenticateUserInput,
    AuthenticateUserUseCase,
    RegisterUserInput,
    RegisterUserUseCase,
)

pytestmark = pytest.mark.django_db


class TestRegisterUserUseCase:
    def test_successful_registration_creates_user_with_hashed_password(self):
        use_case = RegisterUserUseCase(user_service=UserService())

        output = use_case.execute(
            RegisterUserInput(
                email="new@example.com", username="newuser", password="s3cretpass"
            )
        )

        assert output.success
        assert output.user_id is not None
        assert output.error is None

    def test_duplicate_email_rejected(self):
        UserFactory(email="taken@example.com")
        use_case = RegisterUserUseCase(user_service=UserService())

        output = use_case.execute(
            RegisterUserInput(
                email="taken@example.com", username="newuser", password="s3cretpass"
            )
        )

        assert not output.success
        assert output.error == "Email already registered"

    def test_duplicate_username_rejected(self):
        UserFactory(username="takenuser")
        use_case = RegisterUserUseCase(user_service=UserService())

        output = use_case.execute(
            RegisterUserInput(
                email="new@example.com", username="takenuser", password="s3cretpass"
            )
        )

        assert not output.success
        assert output.error == "Username already taken"


class TestAuthenticateUserUseCase:
    def test_successful_authentication_returns_user(self):
        UserFactory(username="alice")
        use_case = AuthenticateUserUseCase(user_service=UserService())

        output = use_case.execute(
            AuthenticateUserInput(username="alice", password="s3cretpass")
        )

        assert output.success
        assert output.user is not None
        assert output.user.username == "alice"

    def test_failed_authentication_returns_generic_error(self):
        UserFactory(username="alice")
        use_case = AuthenticateUserUseCase(user_service=UserService())

        output = use_case.execute(
            AuthenticateUserInput(username="alice", password="wrongpass")
        )

        assert not output.success
        assert output.error == "Invalid credentials"
