from graphene_django import DjangoObjectType
from healthid.apps.profiles.models import Profile


class CustomerProfileType(DjangoObjectType):
    class Meta:
        model = Profile
