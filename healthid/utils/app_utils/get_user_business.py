from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.business.models import UserBusiness


from healthid.apps.outlets.models import OutletUser
from healthid.utils.messages.business_responses import BUSINESS_ERROR_RESPONSES


def get_user_business(user):
    """
    get the logged user's business

    Args:
        user(obj): logged in user

    Returns:
        business(obj): user's business
        graphql error: if use has no business
    """
    business = None
    try:
        business = get_model_object(UserBusiness, 'user_id', user.id).business
        if not business:
            raise GraphQLError(
                BUSINESS_ERROR_RESPONSES["no_business_error"])
        else:
            return business
    except ObjectDoesNotExist:
        return business
