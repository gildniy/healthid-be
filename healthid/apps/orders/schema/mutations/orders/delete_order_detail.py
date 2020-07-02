import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models.orders import OrderDetails
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class DeleteOrderDetail(graphene.Mutation):
    """
    Mutation that deletes one or more records in the 'OrderDetails' model.

    Arguments:
        kwargs(dict): contains the id of the 'OrderDetails'
                        record to be deleted.

    Returns:
        message(str): confirms successful record(s) deletion
    """

    class Arguments:
        order_detail_id = graphene.List(graphene.String, required=True)

    message = graphene.Field(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        order_detail_id = kwargs.get('order_detail_id')
        success_message = SUCCESS_RESPONSES["deletion_success"].format(
            "Product details"
        )
        for order_detail_id in order_detail_id:
            removed_product = get_model_object(
                OrderDetails,
                'id',
                order_detail_id
            )
            removed_product.hard_delete()
        return DeleteOrderDetail(message=success_message)
