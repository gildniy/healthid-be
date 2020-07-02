import graphene
from graphql_jwt.decorators import login_required

from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES

from healthid.apps.orders.models.orders import SupplierOrder


class MarkSupplierOrderAsSent(graphene.Mutation):
    """Mark Supplier Order Details as sent

    Mark BooleanField marked_as_sent

    Args:
        supplier_order_ids: A list of supplier ids and  order ids 
        e.g [{
                supplierId:supplierId(String)
                orderId:orderId(Int)
            }]

    Returns:
        message: a return message.
    """
    message = graphene.String()

    class Arguments:
        supplier_order_ids = graphene.List(graphene.String, required=True)

    @login_required
    def mutate(self, info, **kwargs):
        supplier_order_ids = kwargs.get('supplier_order_ids')
        modified_product_batches = []

        for supplier_order_id in supplier_order_ids:
            # update the information of the corresponding productbatch
            supplier_order = SupplierOrder.objects.get(id=supplier_order_id)
            product_batches = supplier_order.get_product_batches()
            product_batches.update(status='PENDING_DELIVERY')
            # update the product properties of the batch
            for batch in product_batches:
                batch.product.update_autofill_quantity()
            modified_product_batches.extend([batch.id for batch in product_batches])
            # update the status of the order
            supplier_order.status = SupplierOrder.PENDING_DELIVERY
            supplier_order.save()

        message = ORDERS_SUCCESS_RESPONSES[
            "supplier_order_marked_closed"].format(
            ",".join(id for id in modified_product_batches))
        return MarkSupplierOrderAsSent(message=message)
