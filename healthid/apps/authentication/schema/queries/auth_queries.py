import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.models import Role, User
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.authentication_responses import (
    AUTH_ERROR_RESPONSES)
from healthid.apps.authentication.schema.types.user_type import UserType
from healthid.apps.authentication.schema.types.role_type import RoleType


class Query(graphene.AbstractType):
    """
    Query to authenticate a user.
    """
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    role = graphene.Field(
        RoleType, id=graphene.String(), name=graphene.String())
    roles = graphene.List(RoleType)
    online = graphene.String()

    def resolve_online(self, info):
        return "true"

    @login_required
    def resolve_users(self, info):
        """
        Resolver method for users field.
        """
        return User.objects.all()

    @staticmethod
    def resolve_me(self, info):
        """
        Resolver method to check if a user is authenticated.
        """
        user = info.context.user
        if user.is_anonymous:
            login_error = AUTH_ERROR_RESPONSES["authentication_error_response"]
            raise Exception(login_error)
        return user

    @staticmethod
    @login_required
    @user_permission()
    def resolve_role(self, info, **kwargs):
        id = kwargs.get("id")
        name = kwargs.get("name")

        if id is not None:
            return get_model_object(Role, 'id', id)

        if name is not None:
            return get_model_object(Role, 'name', name)
        return None

    @staticmethod
    @login_required
    @user_permission()
    def resolve_roles(self, info, **Kwargs):
        return Role.objects.all()


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    """
    Class to override default JSONWebTokenMutation to
    return the user object along with the authentication token.
    """
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)
