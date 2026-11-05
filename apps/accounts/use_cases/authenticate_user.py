from dataclasses import dataclass

from django.contrib.auth import authenticate

from apps.accounts.models import User
from apps.accounts.services.user_service import UserService


@dataclass(frozen=True, slots=True)
class AuthenticateUserInput:
    username: str
    password: str


@dataclass(frozen=True, slots=True)
class AuthenticateUserOutput:
    success: bool
    user: User | None = None
    error: str | None = None


class AuthenticateUserUseCase:
    def __init__(self, user_service: UserService):
        self._user_service = user_service

    def execute(self, input_dto: AuthenticateUserInput) -> AuthenticateUserOutput:
        authenticated_user = authenticate(
            username=input_dto.username,
            password=input_dto.password,
        )
        if not authenticated_user:
            return AuthenticateUserOutput(success=False, error="Invalid credentials")

        return AuthenticateUserOutput(
            success=True,
            user=authenticated_user,  # type: ignore[arg-type]
        )
