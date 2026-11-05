import pytest
from django.contrib.auth.hashers import check_password
from django.db import IntegrityError

from apps.accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_user_account_persisted(self):
        user = UserFactory()

        assert user.id is not None
        assert user.username
        assert user.email.endswith("@example.com")
        assert user.bio == ""
        assert not user.profile_pic
        assert not user.password.startswith("s3cretpass")
        assert check_password("s3cretpass", user.password)

    def test_email_must_be_unique(self):
        UserFactory(email="taken@example.com")

        with pytest.raises(IntegrityError):
            UserFactory(email="taken@example.com")
