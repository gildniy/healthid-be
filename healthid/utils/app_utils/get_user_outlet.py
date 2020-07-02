from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.business.models import UserBusiness


from healthid.apps.outlets.models import OutletUser
from healthid.utils.messages.business_responses import BUSINESS_ERROR_RESPONSES


def get_user_outlet(user):
    """
    get the logged user's outlet

    Args:
        user(obj): logged in user

    Returns:
        outlet(obj): user's outlet
        graphql error: if use has no outlet
    """
    outlet = None
    try:
        outlet = user.active_outlet
        if not outlet:
            raise GraphQLError(
                BUSINESS_ERROR_RESPONSES["no_outlet_error"])
        else:
            return outlet
    except ObjectDoesNotExist:
        return outlet