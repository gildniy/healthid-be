import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.orders.schema.mutations.orders.initiate_order \
    import InitiateOrder

from healthid.apps.orders.models.orders import (
    Order, OrdersProducts, Suppliers, ProductBatch)
from healthid.utils.app_utils.get_user_business import get_user_business
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.orders.schema.order_query import OrderType
from healthid.apps.products.models import Product
from healthid.apps.products.schema.product_query import AutofillProductType
from healthid.apps.orders.schema.order_query import ProductBatchType
from healthid.utils.messages.common_responses import (
    SUCCESS_RESPONSES, ERROR_RESPONSES)
from healthid.apps.orders.schema.mutations.orders.initiate_order import \
    InitiateOrder


class EditInitiateOrder(graphene.Mutation):
    """
    Mutation to edit an initiated order

    args:
        order_id(int): id of the initiated order to be edited
        name(str): name of the order to edit
        delivery_date(date): expected delivery date
        product_autofill(bool): toggles automatic filling in of the order's
                                products
        supplier_autofill(bool): toggles automatic filling in of the order's
                                 suppliers
        destination_outlet(int): id of the outlet destination

    returns:
        order(obj): 'Order' object detailing the edited order
        success(str): success message confirming edit of the order
    """

    order = graphene.Field(OrderType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        order_id = graphene.Int(required=True)
        name = graphene.String()
        delivery_date = graphene.Date()
        product_autofill = graphene.Boolean()
        supplier_autofill = graphene.Boolean()
        destination_outlet_id = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs['order_id']
        order = get_model_object(Order, 'id', order_id)

        for (key, value) in kwargs.items():
            setattr(order, key, value)

        with SaveContextManager(order) as order:
            success = 'Order Edited Successfully!'
            return InitiateOrder(order=order, success=success)


class EditProductsOrderItem(graphene.Mutation):
    """
    Mutation to edit an autofill generated information table

    args:
        autofill_item_id(int): id of the item in a row
        product_quantity(int): quantity of the product generated
        preferred_supplier_id(int): preferred supplier generated
        backup_supplier_id(int): backup supplier generated

    returns:
        order(obj): 'Order' object detailing the edited order
        success(str): success message confirming edit of the table inforamation
    """

    message = graphene.String()
    error = graphene.String()
    updated_fields = graphene.Field(AutofillProductType)

    class Arguments:
        autofill_item_id = graphene.Int(required=True)
        product_quantity = graphene.Int()
        preferred_supplier_id = graphene.String()
        backup_supplier_id = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        autofill_item_id = kwargs.get("autofill_item_id")
        product_quantity = kwargs.get('product_quantity')
        preferred_supplier_id = kwargs.get('preferred_supplier_id')
        backup_supplier_id = kwargs.get('backup_supplier_id')
        update_fields = get_model_object(
            OrdersProducts, 'id', autofill_item_id)
        product = Product.objects.filter(
            product_name=update_fields.product_name).first()
        if product_quantity:
            if product_quantity > product.reorder_max:
                raise GraphQLError(
                    f"you can not exceed the quantity of {product.reorder_max} of the reoder max")
            update_fields.product_quantity = product_quantity
        if preferred_supplier_id or backup_supplier_id:
            update_fields.current_supplier_id = \
                preferred_supplier_id or backup_supplier_id

        if product_quantity or preferred_supplier_id or backup_supplier_id:
            update_fields.save()
            success = 'successfully edited'
            update_fields = update_fields
            return EditProductsOrderItem(
                updated_fields=update_fields, message=success)
        return {"message": "You did not edit anything"}


class DeleteProductsOrderItem(graphene.Mutation):
    """
    Mutation that deletes one or more records
    in the 'autofill order table' model.

    Arguments:
        kwargs(dict): contains the id of the 'autofill details'
                        record to be deleted.

    Returns:
        message(str): confirms successful record(s) deletion
    """

    class Arguments:
        autofill_item_id = graphene.List(graphene.Int, required=True)

    message = graphene.Field(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        autofill_item_ids = kwargs.get('autofill_item_id')
        success_message = \
            "Product successfully removed from the order list"
        for autofill_item_id in autofill_item_ids:
            remove_item = get_model_object(
                OrdersProducts,
                'id',
                autofill_item_id
            )
            remove_item.is_deleted = True
            remove_item.save()
        return DeleteProductsOrderItem(message=success_message)


class ManualAddingProduct(graphene.Mutation):
    """
    Mutation to add a product manually in the products to be
    initiated table

    args:
        oder_id(int): id of the order
        product_id(int): id of thr product to be added

    returns:
        message(str): success message confirming edit of the table inforamation
        data(obj): 'Product' object detailing the edited product
    """

    message = graphene.String()
    duplicates = graphene.List(ProductBatchType)
    added_product_details = graphene.List(ProductBatchType)

    class Arguments:
        order_id = graphene.Int(required=True)
        product_id = graphene.List(graphene.Int, required=True)

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs.get("order_id")
        product_ids = kwargs.get("product_id")

        order = Order.objects.get(id=order_id)
        business = get_user_business(info.context.user)

        added_batch_products = []
        product_batch_duplicates = []

        if product_ids:
            for product_id in product_ids:
                product = Product.objects.filter(
                    id=product_id).first()

                check_if_product_batch_already_exists = ProductBatch.objects.filter(
                    product_id=product_id, order_id=order_id).first()

                if check_if_product_batch_already_exists:
                    product_batch_duplicates.append(check_if_product_batch_already_exists)

                if product:
                    last_product_batches = ProductBatch.objects.filter(product_id=product_id,
                                                                       business_id=business.id)\
                                                               .order_by('-created_at')[:10]
                    last_unit_costs = list(last_product_batches.values_list('unit_cost', flat=True))
                    last_unit_costs.reverse()
                    last_unit_cost = 0
                    while len(last_unit_costs):
                        last_unit_cost = last_unit_costs.pop()
                        if last_unit_cost > 0:
                            break
                    get_batch_product, create_batch_product = ProductBatch.objects.get_or_create(
                        order_id=order_id,
                        supplier_id=product.preferred_supplier_id or product.backup_supplier_id,
                        product_id=product_id,
                        quantity=product.autofill_quantity,
                        status='PENDING_ORDER',
                        outlet_id=order.destination_outlet_id,
                        business=business,
                        unit_cost=last_unit_cost
                    )

                    if create_batch_product:
                        added_batch_products.append(get_batch_product)

            if added_batch_products:
                no_of_added_batch_products = len(added_batch_products)
                success = f'Successfully added {no_of_added_batch_products} product(s)'
                return ManualAddingProduct(message=success,
                                           added_product_details=added_batch_products,
                                           duplicates=product_batch_duplicates)

            return ManualAddingProduct(
                message="No products added due to duplicates",
                duplicates=product_batch_duplicates)

        return ManualAddingProduct(
            message="No such order found")


class ManualAddingSupplier(graphene.Mutation):
    """
    Mutation to add a product manually in the products to be
    initiated table

    args:
        oder_id(int): id of the order
        product_id(int): id of thr product to be added

    returns:
        message(str): success message confirming edit of the table inforamation
        data(obj): 'Product' object detailing the edited product
    """

    message = graphene.String()
    duplicates = graphene.List(AutofillProductType)
    added_product_details = graphene.List(AutofillProductType)

    class Arguments:
        order_id = graphene.Int(required=True)
        row_ids = graphene.List(graphene.Int, required=True)
        supplier_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        order_id = kwargs.get("order_id")
        row_ids = kwargs.get("row_ids")
        supplier_id = kwargs.get("supplier_id")
        supplier = Suppliers.objects.filter(
            id=supplier_id).first()

        if not supplier:
            return ManualAddingSupplier(
                message="The prodvided supplier does not exist")

        no_of_products = 0
        updatedRecordIds = []
        if row_ids:
            for row_id in row_ids:
                record = OrdersProducts.objects.filter(
                    id=row_id,
                    order_id=order_id).first()

                if record:
                    record.current_supplier_id = supplier_id
                    record.save()
                    no_of_products += 1
                    updatedRecordIds.append(record.id)

            products = OrdersProducts.objects.filter(id__in=updatedRecordIds)

            return ManualAddingSupplier(
                message=f"Successfully assigned {supplier.name} to {no_of_products} products",
                added_product_details=products,
            )
