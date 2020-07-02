import graphene
from graphql_jwt.decorators import login_required

from datetime import datetime

from healthid.apps.orders.models.orders import Order, ProductBatch
from healthid.apps.products.models import Product
from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.orders.schema.order_query import (OrderType, autosuggest_product_order)
from healthid.apps.outlets.models import OutletUser
from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES
from healthid.utils.app_utils.get_user_business import get_user_business


class InitiateOrder(graphene.Mutation):
    """
    Mutation to initiate an order in the database

    args:
        name(str): name of the order to initiate
        delivery_date(date): expected delivery date
        product_autofill(bool): toggles automatic filling in of the order's
                                products
        supplier_autofill(bool): toggles automatic filling in of the order's
                                 suppliers
        destination_outlet(int): id of the outlet destination

    returns:
        order(obj): 'Order' object detailing the created order
        success(str): success message confirming the initiated order
    """

    order = graphene.Field(OrderType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        delivery_date = graphene.Date(required=True)
        product_autofill = graphene.Boolean(required=True)
        supplier_autofill = graphene.Boolean(required=True)
        destination_outlet = graphene.Int(required=True)
        business = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        business = get_user_business(user)
        # get the outlet of the user
        user_outlet = OutletUser.objects.filter(
                user_id=user.id
            ).first()
        # validate if business id passed is valid
        if business.id != kwargs.get('business'):
            raise ValueError('The business ID you provided does not exists')
        outlet = get_model_object(
            Outlet, 'id', kwargs.get('destination_outlet'))
        order = Order(
            name="{0:%d} {0:%B} {0:%Y} {0:%I}:{0:%M}{0:%p}".format(datetime.now()),
            delivery_date=kwargs['delivery_date'],
            product_autofill=kwargs['product_autofill'],
            supplier_autofill=kwargs['supplier_autofill'],
            destination_outlet=outlet,
            user=user,
            business=business,
            outlet=user_outlet.outlet
        )
        with SaveContextManager(order) as order:
            success = ORDERS_SUCCESS_RESPONSES["order_initiation_success"]
            if order.product_autofill:
                autofill_products = autosuggest_product_order(outlet)
                if autofill_products:
                    for p in autofill_products:
                        order_item = ProductBatch()
                        order_item.order = order
                        order_item.product = get_model_object(
                            Product, 'id', p.id
                        )
                        order_item.quantity = p.suggested_quantity
                        order_item.supplier = p.preferred_supplier
                        order_item.preferred_supplier = p.preferred_supplier
                        order_item.backup_supplier = p.backup_supplier
                        order_item.status = 'PENDING_ORDER'
                        order_item.save()

            return InitiateOrder(order=order, success=success)

