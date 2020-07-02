import graphene
import datetime
from graphql_jwt.decorators import login_required
from django.utils.dateparse import parse_date

from healthid.apps.orders.models.orders import OrderDetails
from healthid.apps.orders.models.orders import ProductBatch
from healthid.apps.orders.schema.order_query import ProductBatchType
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.get_user_business import get_user_business
from healthid.utils.app_utils.get_user_outlet import get_user_outlet

class CreateProductBatch(graphene.Mutation):
    """
    creates a batch product

    Args:
        order_id(str): the id of the order
        supplier_id(str): the id if the supplier to be used
        product_id(int): the id of the product 
        batch_ref(str): the batch reference number
        date_received(str): the date of the product
        expiry_date(str): the expiry date of the product
        quantity(int): the quantity of the product
        status(int): the status of hte product
    """

    product_batch = graphene.Field(ProductBatchType)
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_id = graphene.String(required=True)
        product_id = graphene.Int(required=True)
        batch_ref = graphene.String()
        date_received = graphene.String()
        expiry_date = graphene.String()
        quantity = graphene.Int()
        status = graphene.String()
        unit_cost = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        new_product_batch = ProductBatch()
        date_received = kwargs.get("date_received") or datetime.date.today().strftime('%Y-%m-%d')
        expiry_date = kwargs.get("expiry_date") or datetime.date.today() + datetime.timedelta(days=365)

        kwargs['date_received'] = parse_date(date_received)
        kwargs['expiry_date'] = parse_date(expiry_date.strftime('%Y-%m-%d'))

        business = get_user_business(info.context.user)
        outlet = get_user_outlet(info.context.user)

        
        for key, value in kwargs.items():
            setattr(new_product_batch, key, value)

        new_product_batch.business = business
        new_product_batch.outlet = outlet

        with SaveContextManager(new_product_batch, model=ProductBatch) as new_product_batch:
            message = SUCCESS_RESPONSES["creation_success"].format("Batch")
            return CreateProductBatch(message=message,product_batch=new_product_batch)


class updateProductBatch(graphene.Mutation):
    """
    update a batch product

    Args:
        ids(List(str)): the ids of the products to be updated
        order_id(str): the id of the order
        supplier_id(str): the id if the supplier to be used
        product_id(int): the id of the product 
        batch_ref(str): the batch reference number
        date_received(str): the date of the product
        expiry_date(str): the expiry date of the product
        quantity(int): the quantity of the product
        status(int): the status of the product
        unit_cost(int): the unit cost of the product
    """

    product_batches_updated = graphene.List(ProductBatchType)
    message = graphene.String()

    class Arguments:
        ids = graphene.List(graphene.String, required=True)
        outlet_id = graphene.Int()
        order_id = graphene.Int()
        supplier_id = graphene.String()
        product_id = graphene.Int()
        batch_ref = graphene.String()
        date_received = graphene.String()
        expiry_date = graphene.String()
        quantity = graphene.Int()
        status = graphene.String()
        unit_cost = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        ids = kwargs.get("ids")
        product_batches_updated = []

        for product_batch_id in ids:

            existing_product_batch = ProductBatch.objects.get(id=product_batch_id)

            existing_product_batch.order_id = kwargs.get('order_id') or existing_product_batch.order_id 
            existing_product_batch.outlet_id = kwargs.get('outlet_id') or existing_product_batch.outlet_id
            existing_product_batch.supplier_id = kwargs.get('supplier_id') or existing_product_batch.supplier_id
            existing_product_batch.product_id = kwargs.get('product_id') or existing_product_batch.product_id
            existing_product_batch.batch_ref = kwargs.get('batch_ref') or existing_product_batch.batch_ref
            existing_product_batch.date_received = kwargs.get('date_received') or existing_product_batch.date_received
            existing_product_batch.expiry_date = kwargs.get('expiry_date') or existing_product_batch.expiry_date
            existing_product_batch.quantity = kwargs.get('quantity') or existing_product_batch.quantity 
            existing_product_batch.status = kwargs.get('status') or existing_product_batch.status
            existing_product_batch.unit_cost = kwargs.get('unit_cost') or existing_product_batch.unit_cost
            
            with SaveContextManager(existing_product_batch, model=ProductBatch) as updated_product_batch:
                product_batches_updated.append(updated_product_batch)

        message = SUCCESS_RESPONSES["update_success"].format("Batches")
        return updateProductBatch(message = message, product_batches_updated = product_batches_updated)


class deleteProductBatch(graphene.Mutation):
    """
    Delete a batch product

    Args:
    id(str): the id of the product to be updated

    """

    class Arguments:
        ids=graphene.List(graphene.String, required=True)
    
    message = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        ids = kwargs.get('ids')
        success_message = ''
        for batch_id in ids:
            removed_product_batch = get_model_object(
                ProductBatch,
                'id',
                batch_id
            )
            removed_product_batch.hard_delete()
            success_message = SUCCESS_RESPONSES["deletion_success"].format("Batches")

        return deleteProductBatch(message=success_message)