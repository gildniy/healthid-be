import graphene
from graphql import GraphQLError

from healthid.apps.authentication.schema.types.user_type import UserType
from healthid.apps.authentication.models import Role, User
from healthid.utils.app_utils.database import (get_model_object)
from graphql_jwt.decorators import login_required
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.authentication_responses import (
    AUTH_ERROR_RESPONSES)


class UpdateUserRole(graphene.Mutation):
    """
      This class updates the User role
    """

    class Arguments:
        role_id = graphene.String(required=True)
        user_id = graphene.String(required=True)

    success = graphene.Boolean()
    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, **kwargs):
        user_id = kwargs.get('user_id')
        role_id = kwargs.get('role_id')
        user_instance = get_model_object(User, 'id', user_id)
        role_instance = get_model_object(Role, 'id', role_id)
        admin_instance = get_model_object(Role, 'name', 'Master Admin')
        business_users = User.objects.filter(
            business__user=user_instance)
        business_admin = business_users.filter(
            role=admin_instance).count()
        if user_instance.role == role_instance:
            role_error = AUTH_ERROR_RESPONSES["assigning_user_roles"]
            raise GraphQLError(role_error)
        if business_admin == 1 \
                and role_instance != admin_instance:
            downgrade_error = AUTH_ERROR_RESPONSES["downgrade_user"]
            raise GraphQLError(downgrade_error)
        user_instance.role = role_instance
        user_instance.save()
        message = [
            f"Successfully updated {user_instance}"
            f" to a {role_instance} role"
        ]
        return UpdateUserRole(
            user=user_instance,
            message=message)
