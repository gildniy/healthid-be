
from functools import wraps

from graphql import GraphQLError

from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.validator import validator
from healthid.utils.messages.common_responses import ERROR_RESPONSES


class UpdateUser:
    """
    This class contains methods to help with updating of user details.
    """

    def update_user(self, instance, **kwargs):
        password = None
        for key, value in kwargs.items():
            if key == 'password':
                password = value[0].new_password

            if key is not None:
                setattr(instance, key, value)
        instance.set_password(password) if password is not None else None
        instance.save()

    def add_user(self, instance, **kwargs):
        for key, value in kwargs.items():
            if key is not None:
                setattr(instance, key, value)
        instance.save()

    def validate_char(self, **kwargs):
        for key, value in kwargs.items():
            if len(value) > 100 and key != 'profile_image':
                raise GraphQLError(f'Length of {key} cannot '
                                   f'be more than 100 characters')
        return kwargs

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if kwargs.get('mobile_number') is not None:
                mobile_number = kwargs.get('mobile_number')
                validator.validate_mobile(mobile_number)
            if kwargs.get('password') is not None:
                password_input = kwargs.get('password')
                new_password = password_input[0]['new_password']
                validator.validate_password(new_password)
            if kwargs.get('email') is not None:
                email = kwargs.get('email')
                validator.validate_email(email)
            if kwargs.get('username') is not None:
                username = kwargs.get('username')
                validator.validate_username(username)

            if kwargs.get('outlet_id') is not None:
                outlets = kwargs.get('outlet_id')
                if len(outlets) < 1:
                    raise GraphQLError('This user must be assigned '
                                       'to at least 1 (one) outlet')
                for outlet in outlets:
                    if outlet == '':
                        raise GraphQLError(ERROR_RESPONSES[
                                           "empty_field_error"].format(
                                                                 "Outlet Id"))
                    get_model_object(Outlet, 'id', outlet)
            return func(*args, **kwargs)
        return wrapper


user_update_instance = UpdateUser()
