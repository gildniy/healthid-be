from healthid.utils.auth_utils.admin_validation import validate_instance
import graphene

from os import environ, getenv
from healthid.apps.authentication.schema.types.user_type import UserType
from healthid.apps.authentication.models import User
from healthid.utils.app_utils.database import get_model_object
from graphql_jwt.decorators import login_required
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES

DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class UpdateAdminUser(graphene.Mutation):
    user = graphene.Field(UserType)
    success = graphene.Field(graphene.String)

    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        username = graphene.String()
        email = graphene.String()
        mobile_number = graphene.String()
        secondary_email = graphene.String(required=False)
        secondary_phone_number = graphene.String(required=False)

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, **kwargs):
        user = info.context.user
        validated_fields = validate_instance.validate_admin_fields(**kwargs)
        user_instance = get_model_object(User, 'id', user.id)
        for (key, value) in validated_fields.items():
            if key is not None:
                setattr(user_instance, key, value)
        user_instance.save()
        success = SUCCESS_RESPONSES["update_success"].format("Admin Profile")
        return UpdateAdminUser(user=user_instance, success=success)
