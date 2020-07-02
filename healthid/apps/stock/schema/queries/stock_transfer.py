from healthid.apps.stock.schema.mutations.stock_transfer import StockTransferValidator
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.utils.messages.stock_responses import STOCK_ERROR_RESPONSES
from healthid.utils.stock_utils.stock_transfer import StockTransferService
from healthid.utils.stock_utils.validate_stock_transfer import \
    validate
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.stock.schema.types import \
    StockTransferType, StockTransferAggregateType
import graphene
from django.db.models import Q
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.stock.models import StockTransfer


class StockTransferQuery(graphene.ObjectType):
    stock_transfers = graphene.List(StockTransferType)
    stock_transfer = graphene.Field(
        StockTransferType, stock_transfer_id=graphene.String())
    stock_transfer_aggregate = graphene.List(
        StockTransferAggregateType, stock_transfer_id=graphene.String())

    @login_required
    def resolve_stock_transfers(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        stock_transfers = StockTransfer.objects.filter(
            Q(destination_id=outlet.id) | Q(source_id=outlet.id))
        if not stock_transfers:
            raise GraphQLError(STOCK_ERROR_RESPONSES["zero_stock_transfers"])
        return stock_transfers

    @login_required
    def resolve_stock_transfer(self, info, **kwargs):
        """Method to retrieve a single stock transfer using its id
        """
        validate.validate_transfer(kwargs['stock_transfer_id'])
        stock_transfer = get_model_object(
            StockTransfer, 'id', kwargs['stock_transfer_id'])
        StockTransferValidator(stock_transfer, info.context.user) \
            .ensure_user_business_matches_stock_business()
        if not stock_transfer:
            raise GraphQLError(STOCK_ERROR_RESPONSES["inexistent_stock_transfer"])
        else:
            return stock_transfer

    @login_required
    def resolve_stock_transfer_aggregate(self, info, **kwargs):
        stock_transfer = get_model_object(
            StockTransfer, 'id', kwargs['stock_transfer_id'])
        if not stock_transfer:
            raise GraphQLError("The stock transfer Id is not valid")
        StockTransferValidator(stock_transfer, info.context.user) \
            .ensure_user_business_matches_stock_business()
        aggregate_dict = StockTransferService.aggregate_transfer_batches(stock_transfer)
        return list(aggregate_dict.values())
