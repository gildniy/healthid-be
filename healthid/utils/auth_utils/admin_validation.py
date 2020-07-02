
import re

from graphql import GraphQLError
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.authentication_responses import\
      AUTH_ERROR_RESPONSES
from healthid.utils.app_utils.validator import validator


class ValidateAdmin:
    """This class validates user admin fields
    """

    def validate_admin_fields(self, **kwargs):
        secondary_email = kwargs.get('secondary_email', None)
        secondary_phone_number = kwargs.get(
            'secondary_phone_number', None)
        if secondary_email:
            secondary_email = self._validate_secondary_email(
                secondary_email)
        if secondary_phone_number:
            secondary_phone_number = validator.validate_mobile(
                secondary_phone_number)
        first_name = kwargs.get('first_name', '')
        last_name = kwargs.get('last_name', '')
        username = kwargs.get('username', '')
        email = kwargs.get('email', '')
        mobile_number = kwargs.get('mobile_number', '')
        return{
            "first_name": self._validate_name(first_name),
            "last_name": self._validate_name(last_name),
            "username": self._validate_name(username),
            "email": self._validate_secondary_email(email),
            "secondary_email": secondary_email,
            "mobile_number": validator.validate_mobile(
                             mobile_number),
            "secondary_phone_number": secondary_phone_number
        }

    def _validate_name(self, name):

        name = name.strip()
        if not len(name) > 0:
            raise GraphQLError(ERROR_RESPONSES[
                               "empty_field_error"].format("name field"))

        if not len(name) < 30:
            raise GraphQLError(AUTH_ERROR_RESPONSES[
                               "characters_exceed_error"].format("a name"))
        if re.match(r'^[A-Za-z0-9_]*$', name) is None:
            raise GraphQLError(AUTH_ERROR_RESPONSES[
                               "special_characters_error"].format("names"))
        return name

    def _validate_secondary_email(self, email):

        email = email.strip()
        if re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]{2,5}$',
                    email) is None:
            raise GraphQLError(AUTH_ERROR_RESPONSES[
                              "invalid_email_address"].format(email))
        return email


validate_instance = ValidateAdmin()
