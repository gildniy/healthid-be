from graphene_django import DjangoObjectType
from healthid.apps.authentication.models import Role


class RoleType(DjangoObjectType):
    class Meta:
        model = Role
