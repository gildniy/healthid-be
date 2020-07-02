import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import SupplierOrder
from healthid.utils.app_utils.database import SaveContextManager
from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES


class AddOrderNotes(graphene.Mutation):
    """
    Add a note to the supplier order form

    Args:
        supplier_order_id: A supplier order id

    Returns:
        message: a return message.
    """
    message = graphene.String()

    class Arguments:
        supplier_order_id = graphene.String(required=True)
        additional_notes = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        additional_notes = kwargs.get('additional_notes')
        supplier_order_id = kwargs.get('supplier_order_id')
        supplier_order = SupplierOrder.objects.get(id=supplier_order_id)
        if supplier_order and additional_notes:
            supplier_order.additional_notes = additional_notes
            with SaveContextManager(supplier_order,
                                    model=SupplierOrder):
                pass
            message = ORDERS_SUCCESS_RESPONSES[
                "add_order_note_success"]
            return AddOrderNotes(message=message)
        return AddOrderNotes(message="Order Id or \
            additional notes cannot be empty")
