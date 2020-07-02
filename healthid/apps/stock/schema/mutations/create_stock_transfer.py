import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.stock.models import StockTransfer
from healthid.utils.messages.stock_responses import\
    STOCK_ERROR_RESPONSES, STOCK_SUCCESS_RESPONSES
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet


class CloseStockTransfer(graphene.Mutation):
    """Mutation to mark a transfer as complete
    """

    success = graphene.Field(graphene.String)

    class Arguments:
        transfer_number = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        destination_outlet = check_user_has_an_active_outlet(user)
        transfer = StockTransfer.objects.filter(
            id=kwargs['transfer_number'],
            destination_outlet=destination_outlet).first()
        if not transfer:
            raise GraphQLError(STOCK_ERROR_RESPONSES["close_transfer_error"])
        transfer.complete_status = False
        transfer.save()

        success = STOCK_SUCCESS_RESPONSES["stock_transfer_close_success"]
        return CloseStockTransfer(success=success)
