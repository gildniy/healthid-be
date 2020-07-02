import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.stock.models import (
    StockCount,
)

from healthid.apps.stock.schema.types import StockCountType
from healthid.utils.app_utils.database import (
    get_model_object
)
from healthid.utils.app_utils.error_handler import errors
from healthid.utils.messages.stock_responses import (
    STOCK_ERROR_RESPONSES,
    STOCK_SUCCESS_RESPONSES
)

from healthid.utils.stock_utils.stock_count_utils import validate_stock


class RemoveBatchStock(graphene.Mutation):
    """
    Delete a product batch

    args:
        batch_info(list): batch information of the current product stock
        stock_count_id(str): id of the batch stock count

    returns:
        message(str): success message confirming batch deletion
        stock_count(obj): 'StockCount' object containing the
                          stock count details

    """

    stock_count = graphene.Field(StockCountType)

    class Arguments:
        batch_info = graphene.List(graphene.String, required=True)
        stock_count_id = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        batch_info = kwargs.get('batch_info')
        validate_stock.stock_validate(kwargs)
        stock_count_id = kwargs.get('stock_count_id')
        validate_stock.check_empty_id(stock_count_id, name='Stock Count')
        stock_count = get_model_object(
            StockCount, 'id', stock_count_id)
        validate_stock.validate_batch_ids(
            stock_count, batch_info_ids=batch_info)
        if len(stock_count.stock_count_record.values_list('batch_info')) <= 1:
            errors.custom_message(
                STOCK_ERROR_RESPONSES["batch_count_error"])
        for batch_id in batch_info:
            record_instance = stock_count.stock_count_record.get(
                batch_info=batch_id)
            stock_count.stock_count_record.remove(record_instance)
        message = [STOCK_SUCCESS_RESPONSES[
                   "batch_deletion_success"].format(len(batch_info))]
        return RemoveBatchStock(message=message, stock_count=stock_count)
