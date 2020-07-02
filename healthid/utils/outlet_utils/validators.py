import re
from graphql import GraphQLError
from healthid.utils.messages.outlet_responses import \
    OUTLET_ERROR_RESPONSES, OUTLET_SUCCESS_RESPONSES
from healthid.apps.authentication.models import User
from healthid.utils.app_utils.database import get_model_object


class ValidateFields:
    """This class validates a name field, an error
    is raised if a name contains special characters
    """

    def validate_name(self, name, city_country):
        regex = re.compile(r'[@_!#$%^&*()<>?/\|}{~:]')
        if(regex.search(name) is not None) or len(name.strip()) < 1:
            raise GraphQLError(
                OUTLET_ERROR_RESPONSES[
                    "invalid_city_or_country_name"].format(city_country))
        return name


validate_fields = ValidateFields()


def check_user_can_activate_or_deactivate(logged_in_outlet_user):
    """
    Checks if user can activate or deactivate a user in an outlet

    Args:
        logged_in_outlet_user(list): object if logged in user is part of
                                     an outlet else empty list

    Return:
        grapql error: if user is not part or the outlet or is not active
                      in the outlet
    """
    if not logged_in_outlet_user.exists():
        raise GraphQLError(
            OUTLET_ERROR_RESPONSES["logged_in_user_not_in_outlet"])
    if not logged_in_outlet_user.first().is_active_outlet:
        raise GraphQLError(
            OUTLET_ERROR_RESPONSES["logged_in_user_not_active_in_outlet"])


def check_user_can_be_activated_deactivated(outlet,
                                            outlet_user_model,
                                            logged_in_user,
                                            **kwargs):
    """
    function that checks if a user can be activated or deactivated

    Args:
        outlet(obj): outlet in which the user is trying to be activated
                     in or deactivated from
        outlet_user_model(model): OutletUser model
        logged_in_user(obj): Currently logged in user

    Returns:
        message(string), outlet_user(obj): if user can be activated or
                                           deactivated
        graphql error: if user can't be activated or deactivated
    """
    is_active = kwargs.get('is_active')
    user_id = kwargs.get('user_id')
    user = get_model_object(User, 'id', user_id)
    outlet_user = outlet_user_model.objects.filter(
        user=user, outlet=outlet).first()
    logged_in_outlet_user = outlet_user_model.objects.filter(
        user=logged_in_user, outlet=outlet
    )
    check_user_can_activate_or_deactivate(logged_in_outlet_user)
    if not outlet_user:
        raise GraphQLError(OUTLET_ERROR_RESPONSES["user_not_in_outlet"])
    if is_active:
        other_outlets_active_users = outlet_user_model.objects.filter(
            is_active_outlet=True).exclude(outlet=outlet)
        if other_outlets_active_users.filter(user=user).exists():
            raise GraphQLError(
                OUTLET_ERROR_RESPONSES["user_active_in_another_outlet"])
        message = OUTLET_SUCCESS_RESPONSES["activated_user_in_outlet"]
    else:
        if len(outlet.active_outlet_users) <= 1:
            raise GraphQLError(
                OUTLET_ERROR_RESPONSES["one_user_active_in_outlet"])
        message = OUTLET_SUCCESS_RESPONSES["deactivated_user_in_outlet"]
    return message, outlet_user
