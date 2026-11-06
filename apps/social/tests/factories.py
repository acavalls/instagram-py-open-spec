import factory

from apps.accounts.tests.factories import UserFactory
from apps.social.models import Follow


class FollowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Follow

    follower = factory.SubFactory(UserFactory)
    following = factory.SubFactory(UserFactory)
