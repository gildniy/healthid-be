from itertools import compress
from re import sub
import graphene
from django.utils.dateparse import parse_date
from graphql import GraphQLError
from graphql.language import ast
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import BatchInfo, Product, Quantity
from healthid.apps.orders.models.orders import ProductBatch
from healthid.apps.orders.schema.order_query import ProductBatchType
from healthid.apps.products.schema.product_query import (BatchInfoType,
                                                         QuantityType)
from healthid.apps.outlets.models import OutletUser
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.validators import check_validity_of_ids
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.batch_utils import batch_info_instance
from healthid.utils.product_utils.product import \
    generate_reorder_points_and_max
from healthid.utils.messages.products_responses import \
    PRODUCTS_ERROR_RESPONSES, PRODUCTS_SUCCESS_RESPONSES
from healthid.utils.messages.common_responses import \
    SUCCESS_RESPONSES, ERROR_RESPONSES


class ServiceQuality(graphene.types.Scalar):
    """
    Custom type for service Quality rating (integer, range: 1 - 5)
    """
    @staticmethod
    def enforce_int_range(value):
        if isinstance(value, int) and 1 <= value <= 5:
            return value
        raise ValueError(PRODUCTS_ERROR_RESPONSES['invalid_batch_quality'])

    parse_value = enforce_int_range
    serialize = enforce_int_range

    @staticmethod
    def parse_literal(node):
        try:
            value = int(node.value)
            if isinstance(node, ast.IntValue) and 1 <= value <= 5:
                return value
            raise ValueError(PRODUCTS_ERROR_RESPONSES['invalid_batch_quality'])
        except ValueError:
            raise ValueError(PRODUCTS_ERROR_RESPONSES['invalid_batch_quality'])


class CreateBatchInfo(graphene.Mutation):
    """
    Mutation to create a new product batch information

    arguments:
        batch_ref(str): external reference for created batch
        supplier_id(str): id of product supplier
        date_received(str): datte order was received
        product_id(int): id of product to create batch for
        unit_cost(float): id of the product in stock
        quantity(int): quantiy of product received
        expiry_date(str): product expiry date
    returns:
        message(str): success message confirming batch update creation
        productBatch(obj): newly created productBatch details
    """

    product_batch = graphene.Field(ProductBatchType)
    message = graphene.String()

    class Arguments:
        batch_ref = graphene.String()
        supplier_id = graphene.String(required=True)
        date_received = graphene.String(required=True)
        product_id = graphene.Int(required=True)
        unit_cost = graphene.Float(required=True)
        quantity = graphene.Int(required=True)
        expiry_date = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        new_product_batch = ProductBatch()
        user = info.context.user
        quantity = kwargs.pop('quantity')
        kwargs['date_received'] = parse_date(kwargs.get('date_received'))
        kwargs['expiry_date'] = parse_date(kwargs.get('expiry_date'))
        datetime_str = sub('[-]', '', str(kwargs['date_received']))
        batch_ref_auto = f'BN{datetime_str}'
        user_first_assigned_outlet = OutletUser.objects.filter(
            user_id=user.id
        ).first()
        kwargs['outlet_id'] = user_first_assigned_outlet.outlet_id
        kwargs['batch_ref'] = kwargs['batch_ref'] if kwargs['batch_ref'] else batch_ref_auto

        # create a product batch as well
        new_product_batch.outlet_id = kwargs.get('outlet_id')
        new_product_batch.supplier_id = kwargs.get("supplier_id")
        new_product_batch.product_id = kwargs.get("product_id")
        new_product_batch.batch_ref = kwargs.get("batch_ref")
        new_product_batch.date_received = kwargs.get("date_received")
        new_product_batch.expiry_date = kwargs.get("expiry_date")
        new_product_batch.quantity = quantity
        new_product_batch.unit_cost = kwargs.get("unit_cost")
        new_product_batch.status = "IN_STOCK"
        new_product_batch.save()
        # create a product batch as well

        product = Product.objects.get(id = new_product_batch.product_id)
        if product.nearest_expiry_date is None or \
                product.nearest_expiry_date > new_product_batch.expiry_date:
            product.nearest_expiry_date = new_product_batch.expiry_date
            product.save()
        message = SUCCESS_RESPONSES["creation_success"].format("Batch")
        return CreateBatchInfo(message=message, product_batch=new_product_batch)


class ProposeQuantity(graphene.Mutation):
    """
        Mutation to propose a quantity edit to a batch
    """
    batch_info = graphene.List(BatchInfoType)

    class Arguments:
        product_id = graphene.Int(required=True)
        batch_ids = graphene.List(graphene.String, required=True)
        proposed_quantities = graphene.List(graphene.Int, required=True)

    notification = graphene.String()

    @classmethod
    @login_required
    @user_permission('Manager', 'Operations Admin')
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        batch_ids = kwargs.get('batch_ids')
        product_id = kwargs.get('product_id')
        proposed_quantities = kwargs.get('proposed_quantities', None)

        unique_batches_count = len(set(batch_ids))
        if len(batch_ids) != unique_batches_count or \
                len(proposed_quantities) != unique_batches_count:
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["batch_match_error"])
        product = get_model_object(Product, 'id', product_id)
        product_batches = product.get_batches(batch_ids)

        all_proposals = Quantity.get_proposed_quantities()
        pending_request_exists = [
            all_proposals.filter(batch_id=id).exists() for id in batch_ids
        ]
        if any(pending_request_exists):
            pending_proposals = list(
                compress(batch_ids, [item for item in pending_request_exists]))
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["request_approval_error"].format(
                    pending_proposals))

        for batch_id, proposed_quantity in zip(batch_ids, proposed_quantities):
            original_quantity = product.batch_info.get(
                id=batch_id).batch_quantities.get()
            edit_quantity = Quantity(
                batch_id=batch_id, parent=original_quantity, proposed_by=user,
                quantity_remaining=proposed_quantity,
                quantity_received=original_quantity.quantity_received
            )
            with SaveContextManager(edit_quantity, model=Quantity):
                pass
        notification = (PRODUCTS_SUCCESS_RESPONSES["edit_request_success"])
        return cls(batch_info=product_batches, notification=notification)


class ApproveProposedQuantity(graphene.Mutation):
    """
        Mutation to approve or decline a quantity edit to a batch
    """
    quantity_instance = graphene.List(QuantityType)

    class Arguments:
        product_id = graphene.Int(required=True)
        batch_ids = graphene.List(graphene.String, required=True)
        is_approved = graphene.Boolean(required=True)
        comment = graphene.String()

    message = graphene.String()

    @classmethod
    @login_required
    @user_permission('Operations Admin')
    def mutate(cls, root, info, **kwargs):
        approval_status = kwargs.get('is_approved')
        user = info.context.user
        batch_ids = kwargs.get('batch_ids')
        product_id = kwargs.get('product_id')
        comment = kwargs.get('comment', None)

        product = get_model_object(Product, 'id', product_id)
        product_batches = product.get_batches(batch_ids)
        batches_proposals = Quantity.get_proposed_quantities()
        batches_proposals_ids = batches_proposals.values_list(
            'batch_id', flat=True)
        message = PRODUCTS_ERROR_RESPONSES["inexistent_proposal_error"]
        check_validity_of_ids(
            batch_ids, batches_proposals_ids, message=message)

        if not approval_status and not comment:
            raise GraphQLError("Comment please")

        for batch in product_batches:
            date_batch_received = batch.date_received
            original_instance = batch.batch_quantities.get(
                parent_id__isnull=True)
            proposed_instance = batches_proposals.filter(batch=batch).first()
            if approval_status:
                original_instance.quantity_remaining = \
                    proposed_instance.quantity_remaining
                proposed_instance.is_approved = True
            else:
                proposed_instance.request_declined = True
            proposed_instance.authorized_by = user
            proposed_instance.comment = comment
            proposed_instance.save()
            original_instance.save()
            message = (PRODUCTS_SUCCESS_RESPONSES[
                "proposal_approval_success"].format(
                product, date_batch_received)
            ) if approval_status else (
                PRODUCTS_ERROR_RESPONSES[
                    "proposal_decline"].format(product, date_batch_received))

        return cls(message=message, quantity_instance=batches_proposals)
