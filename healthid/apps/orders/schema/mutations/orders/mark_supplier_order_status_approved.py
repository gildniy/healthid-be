import graphene
from graphql_jwt.decorators import login_required

from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.orders.services import SupplierOrderStatusChangeService


class ChangeSupplierOrderStatus(graphene.Mutation):
    """Approve one

    Receive supplier order id.
    Approve the supplier by changing status to approved.

    Args:
        supplier_order_id (str): supplier order id

    Raises:
        GraphQLError: if supplier id doesnot exist in the
            database

    Returns:
        message: message(str)
    """

    message = graphene.Field(graphene.String)

    class Arguments:
        supplier_order_id = graphene.List(graphene.String, required=True)

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        user = info.context.user
        supplier_order_id = kwargs.get('supplier_order_id')

        approval_service = SupplierOrderStatusChangeService(
            supplier_order_id, user)
        message = approval_service.change_status()
        return ChangeSupplierOrderStatus(message=message)
