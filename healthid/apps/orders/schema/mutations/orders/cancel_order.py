import graphene
from graphene import String
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.orders.models.orders import SupplierOrderDetails, Order, ProductBatch, SupplierOrder
from healthid.apps.orders.schema.order_query import SupplierOrderInputType
from healthid.utils.app_utils.database import SaveContextManager
from healthid.utils.app_utils.database import get_model_object


class CancelOrder(graphene.Mutation):
    """Cancel single/multiple supplier order(s) or cancel single/multiple initiated order(s)

    Args:
        supplier_order_ids: A list of supplier order ids
        order_ids: A list of initiated order ids

    Returns:
        message: a return message.
    """
    message = graphene.String()

    class Arguments:
        supplier_order_ids = graphene.List(String)

    @login_required
    def mutate(self, info, **kwargs):
        supplier_order_ids = kwargs.get('supplier_order_ids')
        if supplier_order_ids:
            for supplier_order_id in supplier_order_ids:
                supplier_order = SupplierOrder.objects.get(id=supplier_order_id)
                order = supplier_order.order
                supplier_order_product_batches = supplier_order.get_product_batches()
                if supplier_order_product_batches:
                    supplier_order_product_batches.delete()
                supplier_order.hard_delete()
                number_of_supplier_order_forms = SupplierOrder.objects.filter(
                    order_id=supplier_order.order_id
                ).count()
                if not number_of_supplier_order_forms:
                    order.delete()
        if not supplier_order_ids:
            return CancelOrder(message="No order or supplier specified")
        return CancelOrder(message="Order(s) cancelled successfully")
