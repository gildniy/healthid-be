import re
from itertools import compress
from graphql import GraphQLError
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES
from healthid.utils.messages.validator_responses import VALIDATOR_RESPONSES
from healthid.utils.messages.common_responses import ERROR_RESPONSES


class Validator:
    """
    All validations of fields within the system

    fields:
        email(str): email
        mobile(str): mobile number
        string(str): characters
        new_password(str): password
        field(str): field
        value(str): value
    """

    def validate_email(self, email):
        self.email = email.strip()

        if re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]{2,5}$',
                    self.email) is None:
            raise GraphQLError(ORDERS_ERROR_RESPONSES['invalid_email'])
        return self.email

    def special_character_validation(self, string, field_name=None):
        self.string = re.search(r'[^a-zA-Z0-9.,\-\s]+', string)
        if self.string is not None:
            field = f' in {field_name}' if field_name else ''
            raise GraphQLError(
                VALIDATOR_RESPONSES['character-not-allowed'].format(field))
        return string

    def validate_empty_field(self, field, value):
        """
        Utility method to check if a field value is blank
        and return an error message if it is so.
        """
        self.value = value
        self.field = field
        if self.value == "":
            message = "{} field cannot be blank!".format(self.field)
            raise GraphQLError(message)

    def check_validity_of_ids(self, user_inputs, db_ids, message=None):
        """
        Checks validatity of ids provided by user

        Args:
            user_inputs: Holds a list of ids provided by user
            db_ids: Holds a list of ids that exist in the db
            message: Holds a custom error message(it's optional).

        Raises:
            GraphQLError incase one or more ids provided by user
            is not in the db
        """
        self.user_inputs = user_inputs
        self.db_ids = db_ids
        if not self.user_inputs:
            raise GraphQLError(VALIDATOR_RESPONSES['invalid-batch-id'])

        is_valid = [usr_input in self.db_ids for usr_input in self.user_inputs]

        if not all(is_valid):
            invalid_items = list(
                compress(self.user_inputs, [not item for item in is_valid]))
            if message is None:
                message = VALIDATOR_RESPONSES['invalid-product-id']
            message = message.format(",".join(map(str, invalid_items)))
            raise GraphQLError(message)

    def validate_mobile(self, mobile):
        """
        Validate a string on mobile numbe
        Arguments:
            mobile_number {string} -- [string mobile number format]
        """
        self.mobile = mobile.strip()
        example = "mobile number (ex. +2346787646)"
        if re.match(r'(^[+0-9]{1,3})*([0-9]{10,11}$)',
                    self.mobile) is None:
            raise GraphQLError(
                ERROR_RESPONSES["invalid_field_error"].format(example))
        return self.mobile

    def validate_password(self, password):
        self.password = password.strip()
        regex = re.match('(?=.{8,100})(?=.*[A-Z])(?=.*[0-9])', self.password)
        if regex is None:
            raise GraphQLError(
                'password must have at least 8 characters, '
                'a number and a capital letter.')
        return self.password

    def validate_username(self, username):
        self.username = username.strip()
        if re.match(r'(?=.*^[A-Za-z0-9_\-.]*$)(?=.{1,30})', self.username) is None:
            raise GraphQLError(
                'valid username cannot be blank, contain special characters  '
                'or exceed 30 characters.')
        return self.username


validator = Validator()
