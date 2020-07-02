import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import Quantity
from healthid.apps.stock.models import (
    StockCount,
)

from healthid.apps.stock.schema.types import StockCountType
from healthid.utils.app_utils.database import (
    get_model_object
)
from healthid.utils.app_utils.error_handler import errors
from healthid.utils.app_utils.validators import check_validity_of_ids
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.stock_responses import (
    STOCK_ERROR_RESPONSES,
)


class ReconcileStock(graphene.Mutation):
    """
      Mutation for reconciling stock count.
    """
    stock_count = graphene.Field(StockCountType)
    message = graphene.String()

    class Arguments:
        stock_count_id = graphene.String(required=True)
        batch_info = graphene.List(graphene.String, required=True)
    errors = graphene.List(graphene.String)
    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        batch_info_ids = kwargs.get('batch_info')
        stock_count_id = kwargs.get('stock_count_id')
        if stock_count_id.strip() == "":
            raise GraphQLError(STOCK_ERROR_RESPONSES["invalid_count_field"])
        stock_count = get_model_object(StockCount, 'id', stock_count_id)
        stock_count_batch_ids = stock_count.stock_count_record.values_list(
            'batch_info_id', flat=True)
        message = STOCK_ERROR_RESPONSES["inexistent_batch_error"]
        if stock_count.stock_template.is_closed:
            errors.custom_message(
                STOCK_ERROR_RESPONSES["stock_count_closed"])
        check_validity_of_ids(batch_info_ids, stock_count_batch_ids, message)
        if stock_count.is_approved:
            raise GraphQLError(STOCK_ERROR_RESPONSES["duplication_approval"])
        for batch_id in batch_info_ids:
            stock_record = stock_count.stock_count_record.get(
                batch_info_id=batch_id)
            stock_record_quantity = stock_record.quantity_counted
            quantity = Quantity.objects.get(
                batch_id=batch_id, parent_id__isnull=True)
            quantity.quantity_remaining = stock_record_quantity
            quantity.save()
        stock_count.is_approved = True
        stock_count.save()
        stock_count.update_template_status
        message = SUCCESS_RESPONSES["approval_success"].format("Stock Count")
        return ReconcileStock(message=message, stock_count=stock_count)
