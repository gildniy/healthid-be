import graphene
from graphql_jwt.decorators import login_required
from django.utils.dateparse import parse_date

from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.get_user_business import get_user_business
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)

from healthid.apps.orders.schema.order_query import SupplierOrderType
from healthid.apps.orders.models.orders import SupplierOrder, Order, ProductBatch


class GenerateOrder(graphene.Mutation):
    """
    Given an order id, it generates several supplier order items
    using the productbatches associated with the order

    Args:
        order_id : the id of the order of interest
    """

    supplier_orders = graphene.List(SupplierOrderType)
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        created_supplier_order_list = []
        # get the unique suppliers for the associated product batches
        order_id = kwargs.get("order_id")
        associated_batches = ProductBatch.objects.filter(
            order_id=order_id
        )
        supplier_list = associated_batches.values_list('supplier_id', flat=True)
        unique_suppliers = set(supplier_list)

        # for each unique supplier create a supplier order object
        for unique_supplier in unique_suppliers:
            duplicates = SupplierOrder.objects.filter(
                order_id=order_id,
                supplier_id=unique_supplier
            )
            if not duplicates:
                grand_total = 0
                # get the grand total for each supplier
                for batch in associated_batches.filter(supplier_id=unique_supplier):
                    grand_total += (batch.quantity * batch.unit_cost)
                # create the supplier order item
                new_supplier_order_item = SupplierOrder()
                new_supplier_order_item.order_id = order_id
                new_supplier_order_item.supplier_id = unique_supplier
                new_supplier_order_item.grand_total = grand_total

                with SaveContextManager(new_supplier_order_item, model=SupplierOrder) as new_supplier_order_item:
                    created_supplier_order_list.append(new_supplier_order_item)

        return GenerateOrder(message="Order generated successfully", supplier_orders=created_supplier_order_list)

class CreateSupplierOrder(graphene.Mutation):
    """ 
    creates a supplier order object

    Args:
        order_id : The id of the order involved
        supplier_id: The id of the supplier involved
    """

    supplier_order = graphene.Field(SupplierOrderType)
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs.get("order_id")
        supplier_id = kwargs.get("supplier_id")

        # create the supplier order
        new_supplier_order = SupplierOrder()
        new_supplier_order.order_id = order_id
        new_supplier_order.supplier_id = supplier_id
        with SaveContextManager(new_supplier_order, model=SupplierOrder) as new_supplier_order:
            message = SUCCESS_RESPONSES["creation_success"].format("Suppiier Order")
            return CreateSupplierOrder(message=message, supplier_order=new_supplier_order)


class UpdateSupplierOrder(graphene.Mutation):
    """ 
    update the supplier order object
    Args:
        order_id : The id of the order involved
        supplier_id: The id of the supplier involved
    """

    supplier_order = graphene.Field(SupplierOrderType)
    message = graphene.String()

    class Arguments:
        order_id = graphene.Int(required=True)
        supplier_id = graphene.String(required=True)
        status = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs.get("order_id")
        supplier_id = kwargs.get("supplier_id")
        status = kwargs.get("status")

        existing_supplier_order = SupplierOrder.objects.get(
            order_id=order_id,
            supplier_id=supplier_id
        )
        existing_supplier_order.status = status

        with SaveContextManager(existing_supplier_order, model=SupplierOrder) as existing_supplier_order:
            message = SUCCESS_RESPONSES["update_success"].format("Suppiier Order")
            return CreateSupplierOrder(message=message, supplier_order=existing_supplier_order)


class DeleteSupplierOrder(graphene.Mutation):
    """
    delete a supplier order object
    Args:
        supplier_order_id : the id of the supplier order to be deleted
    """
    message = graphene.String()

    class Arguments:
        supplier_order_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        supplier_order_id = kwargs.get("supplier_order_id")
        removed_supplier_order = get_model_object(
            SupplierOrder,
            'id',
            supplier_order_id
        )
        removed_supplier_order.hard_delete()
        success_message = SUCCESS_RESPONSES["deletion_success"].format("Supplier order")

        return DeleteSupplierOrder(message=success_message)


class SupplierOrderRecieved(graphene.Mutation):
    """
    Mark a supplier order as recieved and update it
    Args:
        additional_notes : notes about the order
        service_quality : a field indicating hte quality of the service recieved
        delivery_promptness : a boolean field indocation as to if the delivery was promt
        supplier_order_id : the id of a suppliadditional_noteser order form
    """

    message = graphene.String()
    supplier_order = graphene.Field(SupplierOrderType)

    class Arguments:
        supplier_order_id = graphene.String(required=True)
        additional_notes = graphene.String()
        service_quality = graphene.Int()
        delivery_promptness = graphene.Boolean()

    @login_required
    def mutate(self, info, **kwargs):
        supplier_order_id = kwargs.get("supplier_order_id")

        recieved_supplier_order = get_model_object(
            SupplierOrder,
            'id',
            supplier_order_id
        )

        recieved_supplier_order.status = 'RECEIVED'
        recieved_supplier_order.additional_notes = kwargs.get("additional_notes")
        recieved_supplier_order.service_quality = kwargs.get("service_quality")
        recieved_supplier_order.delivery_promptness = kwargs.get("delivery_promptness")

        with SaveContextManager(recieved_supplier_order, model=SupplierOrder) as recieved_supplier_order:
            message = SUCCESS_RESPONSES["update_success"].format("Supplier Order")
            return SupplierOrderRecieved(message=message, supplier_order=recieved_supplier_order)
