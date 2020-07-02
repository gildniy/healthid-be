import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.schema.order_query import SupplierOrderDetailsType
from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.orders.services import (SupplierOrderDetailsFetcher,
                                           SupplierOrderDetailsApprovalService)


class ApproveSupplierOrder(graphene.Mutation):
    """Approve one or multple supplier orders

    Receive a list of supplier order ids and order id.
    Make sure the supplier order details are valid and are linked to the
    recieved order.
    Approve the supplier by supplying the approver.

    Args:
        order_id (str): The id for the order
        supplier_order_ids (list: str): A list if supplier order ids
        addtional_notes (str): Additional notes

    Raises:
        GraphQLError: if supplier orders ids do not suppliers ids in the
            database

    Returns:
        supplier_order_details: A list of supplier order details
    """

    message = graphene.Field(graphene.String)
    supplier_order_details = graphene.List(SupplierOrderDetailsType)

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_order_ids = graphene.List(graphene.String)
        additional_notes = graphene.String()
        status = graphene.String()

    @login_required
    @user_permission('Manager', 'Admin')
    def mutate(self, info, **kwargs):
        order_id = kwargs.get('order_id')
        additional_notes = kwargs.get('additional_notes', None)
        supplier_order_ids = kwargs.get('supplier_order_ids')

        user = info.context.user
        orders_fetcher = SupplierOrderDetailsFetcher(order_id,
                                                     supplier_order_ids)
        supplier_orders = orders_fetcher.fetch()
        approval_service = SupplierOrderDetailsApprovalService(
            supplier_orders, user, additional_notes)
        message = approval_service.approve()
        return ApproveSupplierOrder(message=message,
                                    supplier_order_details=supplier_orders)
