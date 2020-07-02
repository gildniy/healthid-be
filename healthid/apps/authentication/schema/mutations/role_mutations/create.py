import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required


from .role_input import RoleInput
from healthid.apps.authentication.schema.types.role_type import RoleType
from healthid.apps.authentication.models import Role
from healthid.utils.app_utils.database import (
    SaveContextManager)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.authentication_responses import (
    AUTH_ERROR_RESPONSES, AUTH_SUCCESS_RESPONSES)


class CreateRole(graphene.Mutation):
    """
        Role creation Mutation
    """

    class Arguments:
        input = RoleInput(required=True)

    success = graphene.Boolean()
    role = graphene.Field(RoleType)
    message = graphene.String()

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, input=None):
        success = True
        if input.name.strip() != "":
            role = Role(name=input.name)
            with SaveContextManager(role, model=Role):
                message = AUTH_SUCCESS_RESPONSES["create_role_success"].format(
                    input.name)
                return CreateRole(success=success, role=role, message=message)
        raise GraphQLError(AUTH_ERROR_RESPONSES["empty_role_name"])
