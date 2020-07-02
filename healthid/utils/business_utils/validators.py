from graphql import GraphQLError

from healthid.utils.app_utils.validator import validator
from healthid.utils.messages.business_responses import BUSINESS_ERROR_RESPONSES
from healthid.utils.messages.common_responses import ERROR_RESPONSES


class ValidateBusiness:
    '''Class to validate the business attributes
    '''

    def validate_business(self, **business_fields):
        '''Method to validate the business attributes
        '''
        validator.validate_email(business_fields['business_email'])
        if not (business_fields['trading_name'] and
                business_fields['legal_name']):
            raise GraphQLError(
                BUSINESS_ERROR_RESPONSES["business_names_validation"])
        elif not business_fields['phone_number']:
            raise GraphQLError(ERROR_RESPONSES[
                               "required_field"].format("Phone number"))
        elif not business_fields['city'] and business_fields['country']:
            raise GraphQLError(BUSINESS_ERROR_RESPONSES[
                "blank_city_and_or_country"])
        elif not business_fields['address_line_1']:
            raise GraphQLError(BUSINESS_ERROR_RESPONSES[
                               "invalid_address1_error"])
