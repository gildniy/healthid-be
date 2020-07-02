import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product
from healthid.apps.stock.models import StockTransfer, StockTransferRecord
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.batch_utils import (
    check_validity_of_ids, check_validity_of_quantity)
from healthid.utils.stock_utils.validate_stock_transfer import validate
from healthid.utils.messages.stock_responses import\
    STOCK_ERROR_RESPONSES, STOCK_SUCCESS_RESPONSES
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.apps.stock.schema.types import StockTransferType


class OpenStockTransfer(graphene.Mutation):
    """Mutation to open a stock transfer
    """

    stock_transfer = graphene.Field(StockTransferType)
    success = graphene.List(graphene.String)

    class Arguments:
        batch_ids = graphene.List(graphene.String, required=True)
        product_id = graphene.Int(required=True)
        quantities = graphene.List(graphene.Int, required=True)
        destination_outlet_id = graphene.Int(required=True)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        user = info.context.user

        validate.validate_fields(**kwargs)
        product_id = kwargs['product_id']
        batch_ids = kwargs['batch_ids']
        quantities = kwargs['quantities']

        product = get_model_object(Product, 'id', product_id)
        sending_outlet = check_user_has_an_active_outlet(user)
        destination_outlet = get_model_object(
            Outlet, 'id', kwargs['destination_outlet_id'])
        if str(sending_outlet) == str(destination_outlet):
            raise GraphQLError(
                STOCK_ERROR_RESPONSES["same_origin_stock_transfer"])
        product_batch_ids = product.batch_info.values_list("id", flat=True)

        message = "Batch with ids {} do not exist in this product"
        check_validity_of_ids(batch_ids, product_batch_ids, message=message)
        product_batch_quantities = [product.batch_info.get(
            id=id).quantity for id in batch_ids]

        check_validity_of_quantity(
            quantities, product_batch_quantities, batch_ids)

        stock_transfer = StockTransfer(
            product=product,
            sending_outlet=sending_outlet,
            destination_outlet=destination_outlet
        )

        with SaveContextManager(stock_transfer) as stock_transfer:
            for index, value in enumerate(batch_ids):
                stock_transfer_record = StockTransferRecord.objects.create(
                    quantity=quantities[index],
                    batch_id=value
                )
                stock_transfer.stock_transfer_record.add(stock_transfer_record)

        success = [STOCK_SUCCESS_RESPONSES["stock_transfer_open_success"]]
        return OpenStockTransfer(
            stock_transfer=stock_transfer, success=success)
