import graphene
import datetime

from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from graphene_django import DjangoObjectType
from re import sub
from healthid.apps.orders.models.orders import SupplierOrderDetails, Order, SupplierOrder
from healthid.apps.products.schema.product_query import BatchInfoType
from healthid.apps.products.models import BatchInfo, Quantity
from healthid.apps.orders.models.orders import ProductBatch
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.orders.services import OrderStatusChangeService
from django.utils.dateparse import parse_date


class BatchInfoObject(graphene.InputObjectType):
    notes = graphene.String()
    date_received = graphene.String(required=True)
    delivery_promptness = graphene.Boolean(required=True)
    expiry_date = graphene.String(required=True)
    product_id = graphene.Int(required=True)
    quantity_received = graphene.Int(required=True)
    service_quality = graphene.Int(required=True)
    supplier_id = graphene.String(required=True)
    cost_per_item = graphene.Int(required=True)
    batch_no = graphene.String()


class CloseOrder(graphene.Mutation):
    """
    Mutation to initiate closing an open order in the database

     arguments:
         order_id(int): name of the order to initiate

     returns:
        message(str): message containing operation response
    """
    message = graphene.String()

    class Arguments:
        supplier_order_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        supplier_order_id = kwargs.get('supplier_order_id')
        supplier_order = SupplierOrder.objects.get(id=supplier_order_id)
        order = supplier_order.order
        supplier_order_product_batches = supplier_order.get_product_batches()
        if not supplier_order_product_batches:
            raise GraphQLError("You cannot close an empty order.")
        else:
            products_received = 0
            time = datetime.datetime.now()
            datetime_str = sub('[-]', '', time.strftime("%Y%m%d%H%M"))
            batch_no_auto = f'BN{datetime_str}'

            reconciled_statuses = [
                'CANCELLED',
                'NOT_RECEIVED',
                'RETURNED',
                'IN_STOCK'
            ]
            unreconciled_items = []
            for product_batch in supplier_order_product_batches:
                if product_batch.batch_ref is None:
                    product_batch.batch_ref = batch_no_auto

                product_batch.outlet = order.destination_outlet
                product_batch.save()

                if product_batch.status not in reconciled_statuses:
                    unreconciled_items.append(product_batch)
                
                if product_batch.status == "IN_STOCK":
                    product_batch.product.update_inventory()

                products_received = products_received + 1

        if unreconciled_items:
            raise GraphQLError(f"You cannot close an order with unreconciled items.")
        else:
            supplier_order.status = 'CLOSED'
            supplier_order.save()
            return CloseOrder(message=f"Supplier Order has been closed successfully. {products_received} products received.")