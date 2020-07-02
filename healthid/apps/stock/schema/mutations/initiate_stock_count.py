import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import Product
from healthid.apps.stock.models import (
    StockCount,
    StockCountRecord,
    StockCountTemplate
)

from healthid.apps.stock.schema.types import StockCountType
from healthid.utils.app_utils.database import (
    SaveContextManager,
    get_model_object
)
from healthid.utils.app_utils.error_handler import errors
from healthid.utils.app_utils.validators import check_validity_of_ids
from healthid.utils.messages.stock_responses import (
    STOCK_ERROR_RESPONSES,
    STOCK_SUCCESS_RESPONSES
)
from healthid.utils.notifications_utils.handle_notifications import notify
from healthid.utils.stock_utils.stock_count_utils import validate_stock


class VarianceEnum(graphene.Enum):
    IncorrectInitialEntry = 'Incorrect Initial Entry'
    ReturnedToDistributor = 'Returned to Distributor'
    DamagedProduct = 'Damaged Product'
    WrongSale = 'Wrong Sale'
    UnIdentified = 'Unidentified'
    NoVariance = 'No Variance'
    Others = 'Others'


class InitiateStockCount(graphene.Mutation):
    """
    Mutation to initialize Stock Count Information

    args:
        batch_info(list): batch information of the current product stock
        stock_count_id(str): id of the stock count to be updated
        stock_template_id(int): id of the stock template used for the update
        product(int): id of the product in stock
        quantity_counted(list): quantity of product per batch
        variance_reason(str): describes source of stock amount variance
        remarks(str): batch notes
        specify_reason(str): provides justification for stock initiation
        is_completed(boolean): toggle update completion
        is_closed(boolean): toggle stock template access

    returns:
        success(str): success message confirming stock update completion
        stock_count(obj): 'StockCount' object containing the
                          stock count details
    """

    stock_count = graphene.Field(StockCountType)

    class Arguments:
        batch_info = graphene.List(graphene.String, required=True)
        stock_template_id = graphene.Int(required=True)
        product = graphene.Int(required=True)
        quantity_counted = graphene.List(graphene.Int, required=True)
        variance_reason = graphene.Argument(VarianceEnum, required=True)
        remarks = graphene.String()
        specify_reason = graphene.String()
        is_completed = graphene.Boolean(required=True)
        is_closed = graphene.Boolean()

    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @login_required
    def mutate(self, info, **kwargs):
        validate_stock.stock_validate(kwargs)
        batch_info = kwargs.get('batch_info')
        quantity_counted = kwargs.get('quantity_counted')
        product_id = kwargs.get('product')
        is_closed = kwargs.get('is_closed', False)
        product = get_model_object(Product, 'id', product_id)
        product_batches = product.batch_info.all().values_list('id', flat=True)
        stock_template = get_model_object(
            StockCountTemplate, 'id', kwargs.get('stock_template_id'))
        if stock_template.is_closed:
            errors.custom_message(
                STOCK_ERROR_RESPONSES["stock_count_closed"])
        stock_template_products = stock_template.products.all()
        if product not in stock_template_products:
            errors.custom_message(
                STOCK_ERROR_RESPONSES["product_template_error"])

        message = f'Product {product.product_name} ' + \
            STOCK_ERROR_RESPONSES["product_batch_id_error"]
        check_validity_of_ids(batch_info, product_batches, message=message)

        stock_count = StockCount()
        validate_stock.add_stock(kwargs, stock_count)
        with SaveContextManager(stock_count) as stock_count:
            message = [STOCK_SUCCESS_RESPONSES[
                       "stock_account_save_in_progress"]]
            for index, value in enumerate(batch_info):
                record_instance = StockCountRecord.objects.create(
                    quantity_counted=quantity_counted[index],
                    batch_info_id=value,
                )
                stock_count.stock_count_record.add(record_instance)
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
                message = [STOCK_SUCCESS_RESPONSES["stock_approval_success"]]
            stock_template.is_closed = is_closed
            stock_template.save()
            stock_count.update_template_status
        return InitiateStockCount(message=message, stock_count=stock_count)
