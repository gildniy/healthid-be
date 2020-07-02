import re
from itertools import compress
from dateutil import parser

from django.utils.timezone import make_aware

from graphql import GraphQLError


def validate_email(email):
    email = email.strip()

    if re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]{2,5}$',
                email) is None:
        raise GraphQLError('Please input a valid email'.format(email))
    return email


def special_cahracter_validation(string):
    string_regex = re.search(r'[^a-zA-Z0-9.,\-\s]+', string)
    if string_regex is not None:
        raise GraphQLError("special characters not allowed")


def validate_password(new_password):
    password_regex = '(?=.{8,100})(?=.*[A-Z])(?=.*[0-9])'
    if re.match(password_regex, new_password) is None:
        error = ('password must have at least 8 characters,'
                 ' a number and a capital letter.')
        return error


def validate_empty_field(field, value):
    """
    Utility method to check if a field value is blank
    and return an error message if it is so.
    """
    if value.strip() == "":
        message = "{} field cannot be blank!".format(field)
        raise GraphQLError(message)


def check_validity_of_ids(user_inputs, db_ids, message=None):
    """
    Checks validatity of ids provided by user

    Args:
        user_inputs: Holds a list of ids provided by user
        db_ids: Holds a list of ids that exist in the db
        message: Holds a custom error message(it's optional).

    Raises:
        GraphQLError incase one or more ids provided by user is not in the db
    """
    if not user_inputs:
        raise GraphQLError('Please provide atleast one batch id.')

    is_valid = [user_input in db_ids for user_input in user_inputs]

    if not all(is_valid):
        invalid_items = list(
            compress(user_inputs, [not item for item in is_valid]))
        if message is None:
            message = "Products with ids '{}' do not exist in this batch"
        message = message.format(",".join(map(str, invalid_items)))
        raise GraphQLError(message)


def validate_date(string_date):
    """
    Converts a string date into a python date object

    Arguments:
        string_date {string} -- [sting date format]
    """
    valid_date = make_aware(parser.parse(string_date))
    return valid_date


def validate_expire_months(month):
    """
    Validates expiration months

    Arguments:
        month {integer} -- [1 to 12]
    """
    if not month or month < 0 or month > 12:
        expire_months = 12
    else:
        expire_months = month
    return expire_months


def validate_mobile(mobile):
    """
    Validate mobile number

    Arguments:
        mobile_number {string} -- [string mobile number format]
    """
    return re.match(r'(^[+0-9]{1,3})*([0-9]{7,15}$)', str(mobile).strip())
