import graphene
from graphql import GraphQLError


from .password_input import PasswordInput
from os import environ, getenv
from healthid.apps.authentication.schema.types.user_type import UserType
from healthid.apps.authentication.models import User
from healthid.utils.messages.authentication_responses import (
    AUTH_ERROR_RESPONSES)
from graphql_jwt.decorators import login_required
from healthid.utils.auth_utils import user_update_instance
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES

DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class UpdateUserDetails(graphene.Mutation):
    """
    mutation to update user details
    """

    class Arguments:
        mobile_number = graphene.String()
        password = graphene.List(PasswordInput)
        username = graphene.String()
        profile_image = graphene.String()
        email = graphene.String()
        email_notification_permissions = graphene.Boolean()

    user = graphene.Field(UserType)
    error = graphene.Field(graphene.String)
    success = graphene.Field(graphene.String)

    @login_required
    @user_update_instance
    def mutate(self, info, **kwargs):
        user = info.context.user
        if kwargs.get('password') is not None:
            password_input = kwargs.get('password')
            old_password = password_input[0].old_password
            check_old_password = user.check_password(old_password)
            if not check_old_password:
                error_message = AUTH_ERROR_RESPONSES["password_match_error"]
                raise GraphQLError(error_message)
        if kwargs.get('email') is not None:
            email = kwargs.get('email')
            if User.objects.filter(email=email):
                email_error = AUTH_ERROR_RESPONSES["email_duplicate_error"]
                raise GraphQLError(email_error)

        user_update_instance.update_user(user, **kwargs)
        success = SUCCESS_RESPONSES["update_success"].format(user.username)
        return UpdateUserDetails(
            success=success, error=None, user=user)
