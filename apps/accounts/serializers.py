from rest_framework import serializers

from apps.accounts.models import User


class UserCreateSerializer(serializers.Serializer):
    """Write serializer — validates registration input."""

    email = serializers.EmailField()
    username = serializers.CharField(max_length=150, min_length=3)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value: str) -> str:
        if not value.isalnum():
            raise serializers.ValidationError(
                "Username must contain only letters and numbers"
            )
        return value


class UserReadSerializer(serializers.ModelSerializer):
    """Read serializer — formats user output."""

    class Meta:
        model = User
        fields = ["id", "email", "username", "bio", "updated_at"]
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    """Write serializer — validates login input."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
