import graphene

from .role_input import RoleInput
from healthid.apps.authentication.schema.types.role_type import RoleType
from healthid.apps.authentication.models import Role
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)
from graphql_jwt.decorators import login_required
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class EditRole(graphene.Mutation):
    """
        Role Edit Mutation
    """

    class Arguments:
        id = graphene.String(required=True)
        input = RoleInput(required=True)

    success = graphene.Boolean()
    role = graphene.Field(RoleType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, id, input=None):
        success = False
        role_instance = get_model_object(Role, 'id', id)
        role_instance.name = input.name
        with SaveContextManager(role_instance, model=Role):
            success = True
            edit_success = SUCCESS_RESPONSES["update_success"]
            message = [edit_success.format(role_instance.name)]
            return EditRole(
                success=success, role=role_instance, message=message
            )
