import graphene
import cloudinary
import cloudinary.api
import cloudinary.uploader

from os import environ, getenv
from healthid.apps.authentication.schema.types.user_type import UserType
from healthid.apps.authentication.models import User
from healthid.utils.app_utils.database import get_model_object
from graphql_jwt.decorators import login_required
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.auth_utils import user_update_instance
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES

DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class AdminUpdateUserDetails(graphene.Mutation):
    """
        Admin update some specific fields in the user profile
    """

    class Arguments:
        id = graphene.String(required=True)
        job_title = graphene.String()
        starting_date = graphene.String()
        email = graphene.String(required=True)
        mobile_number = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        username = graphene.String()
        profile_image = graphene.String()
        birthday = graphene.String()

    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    @user_update_instance
    @user_permission()
    def mutate(self, info, **kwargs):
        profile_image = kwargs.get('profile_image')
        data = {
            'email': kwargs.get('email'),
            'mobile_number': kwargs.get('mobile_number'),
            'first_name': kwargs.get('first_name'),
            'last_name': kwargs.get('last_name'),
            'username': kwargs.get('username'),
            'job_title': kwargs.get('job_title'),
            'starting_date': kwargs.get('starting_date'),
            'birthday': kwargs.get('birthday'),
        }
        user_id = kwargs.get('id')
        user = get_model_object(User, 'id', user_id)
        user_update_instance.add_user(user, **data)
        if profile_image:
            user.profile_image = \
                cloudinary.uploader.upload(profile_image).get('url')
        user.save()
        update_message = SUCCESS_RESPONSES["update_success"]
        message = [
            update_message.format(user.username)
        ]
        return AdminUpdateUserDetails(message=message, user=user)
