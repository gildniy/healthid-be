from graphql import GraphQLError
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.outlets.models import Outlet, OutletUser
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


def check_user_is_active_in_outlet(user, outlet_id=None, outlet=None):
    """
    checks if user is active in an outlet

    Args:
        user(obj): user to be checked if their active in an outlet
        outlet_id(int): id of outlet to check if user is active in
        outlet(obj): outlet to check if user is active in

    Returns:
        graphql error: if user is not active in outlet
        outlet(obj): if user is active in that outlet
    """
    if outlet_id:
        outlet = get_model_object(Outlet, 'id', outlet_id)
    active_outlet = check_user_has_an_active_outlet(user)
    if active_outlet.id != outlet.id:
        raise GraphQLError(
            OUTLET_ERROR_RESPONSES["logged_in_user_not_active_in_outlet"])
    return outlet


def check_user_has_an_active_outlet(user):
    """
    checks if logged in user is active in any outlet
    Args:
        user(obj): logged in user
    Returns:
        active_outlet(obj): outlet user is active in
        graphql error: if use is not active in any outlet
    """
    active_outlet = user.active_outlet
    if not active_outlet:
        raise GraphQLError(
            OUTLET_ERROR_RESPONSES["user_not_active_in_any_outlet"])
    return active_outlet


def get_user_active_outlet(user, outlet_id):
    """
    check whether the user owns an outlet before updated:

    Args:
        user(obj): user to be checked if their active in an outlet
        outlet_id(int): id of outlet to check if user is active in
    """
    outlet_user = OutletUser.objects.filter(
        outlet_id=outlet_id, user=user, is_active_outlet=True).first()
    if outlet_user:
        if outlet_user.user.role.name == "Master Admin":
            return outlet_user.outlet
        else:
            raise GraphQLError(OUTLET_ERROR_RESPONSES["user_not_the_owner"])
    else:
        raise GraphQLError(
            OUTLET_ERROR_RESPONSES["user_not_active_in_any_outlet"])
