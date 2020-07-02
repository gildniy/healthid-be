from healthid.apps.preference.models import OutletPreference
from graphql import GraphQLError
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


def get_outlet_preference_by_user(user):
    """
        Method to return outlet preference user is active to
    Args:
        user(obj): user context
    Returns:
        outlet_preference(obj): if user is active to an outlet
        None: if user is not active to any outlet
    """
    outlet_user = user.outletuser_set.filter(is_active_outlet=True)
    if outlet_user.exists():
        outlet_id = outlet_user.first().outlet_id
        outlet_preference = OutletPreference.objects.filter(
            outlet_id=outlet_id).first()
        return outlet_preference
    return None


def get_user_outlet_currency_id(user):
    """
        Method to return outlet currency id user is active to
    Args:
        user(obj): user context
    Returns:
        outlet_currency_id(string): if user is active to an outlet
        otherwise a GraphQLError is raised
    """
    outlet_preference = get_outlet_preference_by_user(user)
    if outlet_preference is None:
        raise GraphQLError(
            OUTLET_ERROR_RESPONSES[
                "user_not_active_in_any_outlet"
            ])
    return outlet_preference.outlet_currency_id
