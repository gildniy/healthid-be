import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.stock.models import (
    StockCount,
)

from healthid.apps.stock.schema.types import StockCountType
from healthid.utils.app_utils.database import (
    SaveContextManager,
    get_model_object
)
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.notifications_utils.handle_notifications import notify
from healthid.utils.stock_utils.stock_count_utils import validate_stock
from healthid.apps.stock.schema.mutations.initiate_stock_count \
    import VarianceEnum


class UpdateStockCount(graphene.Mutation):
    """
    Update stock count.

    args:
        batch_info(list): batch information of the current product stock
        stock_count_id(str): id of the stock count to be updated
        stock_template_id(int): id of the stock template used for the update
        product(int): id of the product in stock
        quantity_counted(list): amount of counted product stock
        variance_reason(str): describes source of stock variance
        remarks(str): batch notes
        specify_reason(str): provide justification for stock update
        is_completed(boolean): toggle update completion

    returns:
        success(str): success message confirming stock update completion
        stock_count(obj): 'StockCount' object containing the
                          stock count details
    """

    stock_count = graphene.Field(StockCountType)

    class Arguments:
        batch_info = graphene.List(graphene.String)
        stock_count_id = graphene.String(required=True)
        stock_template_id = graphene.Int()
        product = graphene.Int()
        quantity_counted = graphene.List(graphene.Int)
        variance_reason = graphene.Argument(VarianceEnum)
        remarks = graphene.String()
        specify_reason = graphene.String()
        is_completed = graphene.Boolean()

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        batch_info = kwargs.get('batch_info')
        quantity_counted = kwargs.get('quantity_counted')
        stock_count_id = kwargs.get('stock_count_id')
        validate_stock.stock_validate(kwargs)
        validate_stock.check_empty_id(stock_count_id, name='Stock Count')
        stock_count = get_model_object(StockCount, 'id', stock_count_id)
        validate_stock.check_approved_stock(info, stock_count)
        validate_stock.add_stock(kwargs, stock_count)
        validate_stock.validate_batch_ids(stock_count, batch_info)
        with SaveContextManager(stock_count) as stock_count:
            if batch_info and quantity_counted:
                for field, data in enumerate(batch_info):
                    record_instance = \
                        stock_count.stock_count_record.get(batch_info=data)
                    record_instance.quantity_counted = \
                        quantity_counted[field]
                    record_instance.save()
            if stock_count.is_completed:
                users_instance = \
                    stock_count.stock_template.designated_users.all()
                email_stock_count = \
                    'email_alerts/stocks/stock_count_email.html'
                event_name = 'stock_count_approval'
                subject = 'Stock Count sent for approval'
                context = {
                    'template_type': 'Stock Count Approval',
                    'small_text_detail': 'Stock Count Details',
                    'email': str(info.context.user.email),
                    'quantity_counted': str(stock_count.quantity_counted),
                    'variance_reason': str(stock_count.variance_reason),
                    'product_quantity':
                    str(stock_count.product.quantity_in_stock)
                }
                notify(
                    users=users_instance,
                    subject=subject,
                    event_name=event_name,
                    body=context,
                    html_subject=context,
                    html_body=email_stock_count,
                )
        message = [SUCCESS_RESPONSES["update_success"].format("Stock Count")]
        return UpdateStockCount(
            message=message, stock_count=stock_count)
