from uuid import UUID

from apps.accounts.models import User


class UserService:
    """Domain logic for User operations."""

    @staticmethod
    def get_by_id(user_id: UUID) -> User | None:
        return User.objects.filter(id=user_id).first()

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return User.objects.filter(email=email).first()

    def create_user(self, email: str, username: str, password: str) -> User:
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
        )
