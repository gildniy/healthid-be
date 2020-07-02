import graphene
from graphql_jwt.decorators import login_required
from healthid.apps.stock.models import (
    StockCount,
)

from healthid.apps.stock.schema.types import StockCountType
from healthid.utils.app_utils.database import (
    get_model_object
)
from healthid.utils.messages.stock_responses import (
    STOCK_SUCCESS_RESPONSES
)
from healthid.utils.stock_utils.stock_count_utils import validate_stock


class DeleteStockCount(graphene.Mutation):
    """
    Delete a product's batch info

    args:
        stock_count_id(str): id of the batch stock count to be deleted

    returns:
        message(str): success message confirming stock deletion
        stock_count(obj): 'StockCount' object containing the
                          stock count details

    """

    stock_count = graphene.Field(StockCountType)

    class Arguments:
        stock_count_id = graphene.String(required=True)

    errors = graphene.List(graphene.String)
    message = graphene.String()

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        user = info.context.user
        stock_count_id = kwargs.get('stock_count_id')
        validate_stock.check_empty_id(stock_count_id, name='Stock Count')
        stock_count = get_model_object(StockCount, 'id', stock_count_id)
        validate_stock.check_approved_stock(info, stock_count)
        message = STOCK_SUCCESS_RESPONSES[
            "stock_count_delete_success"].format(stock_count.id)
        stock_count.delete(user)
        return DeleteStockCount(message=message)
