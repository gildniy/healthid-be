from graphql import GraphQLError
from healthid.utils.messages.events_responses import EVENTS_ERROR_RESPONSES


class ValidateAdmin():
    '''Class to validate the admin status of an event creator
    '''
    permitted_roles = ['Master Admin', 'Manager']

    def validate_master_admin(self, user, event_type):
        if str(user.role) != 'Master Admin' and event_type == 'Business':
            raise GraphQLError(EVENTS_ERROR_RESPONSES[
                               "business_operations_validation_error"])
        elif (str(user.role) not in self.permitted_roles and event_type ==
              'Outlet'):
            raise GraphQLError(EVENTS_ERROR_RESPONSES[
                               "outlet_operations_validation_error"])
