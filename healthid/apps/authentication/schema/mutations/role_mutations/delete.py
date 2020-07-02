import graphene

from healthid.apps.authentication.schema.types.role_type import RoleType
from healthid.apps.authentication.models import Role
from healthid.utils.app_utils.database import (get_model_object)
from graphql_jwt.decorators import login_required
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class DeleteRole(graphene.Mutation):
    """
        Role Delete Mutation
    """

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()
    role = graphene.Field(RoleType)
    errors = graphene.List(graphene.String)
    message = graphene.String()

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, id):
        role_instance = get_model_object(Role, 'id', id)
        success = True
        message =\
            SUCCESS_RESPONSES["deletion_success"].format(role_instance.name)
        role_instance.delete()
        return DeleteRole(success=success, message=message)
