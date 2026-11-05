from dataclasses import dataclass
from uuid import UUID

from apps.accounts.models import User
from apps.accounts.services.user_service import UserService


@dataclass(frozen=True, slots=True)
class RegisterUserInput:
    email: str
    username: str
    password: str


@dataclass(frozen=True, slots=True)
class RegisterUserOutput:
    success: bool
    user_id: UUID | None = None
    error: str | None = None


class RegisterUserUseCase:
    def __init__(self, user_service: UserService):
        self._user_service = user_service

    def execute(self, input_dto: RegisterUserInput) -> RegisterUserOutput:
        is_valid, error = User.validate_registration(
            email=input_dto.email,
            username=input_dto.username,
        )
        if not is_valid:
            return RegisterUserOutput(success=False, error=error)

        user = self._user_service.create_user(
            email=input_dto.email,
            username=input_dto.username,
            password=input_dto.password,
        )
        return RegisterUserOutput(success=True, user_id=user.id)
