from graphql import GraphQLError
from healthid.utils.app_utils.error_handler import errors
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.products.models import BatchInfo, Product
from healthid.apps.stock.models import StockCountTemplate


class ValidateStockCount:
    """
    This method contains methods to initiate a stock count
    """

    def check_approved_stock(self, info, instance):
        user = info.context.user
        if instance.is_approved:
            allowed_role = ('Master Admin', 'Operations Admin')
            if str(user.role) not in allowed_role:
                message = "Permission denied. You don't have " \
                          "access to this functionality"
                errors.custom_message(message)

    def validate_list(self, **data):
        batch_info = data.get('batch_info')
        quantity_counted = data.get('quantity_counted')
        valid_list = len(batch_info) == len(quantity_counted)
        if not valid_list or len(batch_info) < 1:
            raise GraphQLError('All list input must have the same length')

    def check_empty_id(self, param, name):
        if param.strip() in ('', None):
            errors.custom_message(
                f'{name} Id cannot be empty')

    def stock_validate(self, kwargs):
        variance_reason = kwargs.get('variance_reason')
        specific_reason = kwargs.get('specify_reason')
        if variance_reason and variance_reason == 'Others':
            if specific_reason in ('', None):
                message = "Specify the variance reason."
                errors.custom_message(message)

    def validate_batch_ids(self, stock_count, batch_info_ids):
        stock_count_batches = \
            stock_count.stock_count_record.values_list(
                'batch_info', flat=True)
        if not all(
                [batch_info_id in stock_count_batches
                 for batch_info_id in batch_info_ids]):
            errors.custom_message(
                'All Batches must belong to this stock count')

    def add_stock(self, kwargs, stock_count):
        batch_info_ids = kwargs.get('batch_info')
        quantity_counted = kwargs.get('quantity_counted')
        variance_reason = kwargs.get('variance_reason')
        data = {
            'batch_info': batch_info_ids,
            'quantity_counted': quantity_counted,
        }
        validate_stock.validate_list(**data)
        if batch_info_ids:
            for index, value in enumerate(batch_info_ids):
                self.check_empty_id(value, name='Batch_info')
                batch_instance = get_model_object(BatchInfo, 'id', value)
                if quantity_counted and quantity_counted[index] < 0:
                    message = \
                        f"Quantity Counted for batch {batch_instance} " \
                        f"cannot be less than Zero (0)"
                    errors.custom_message(message)
                if not batch_instance.quantity == quantity_counted \
                        and variance_reason == 'No Variance':
                    message = "There is a variance, " \
                              "Kindly state the variance reason"
                    errors.custom_message(message)
        for (field, value) in kwargs.items():
            if field == 'stock_template':
                value = get_model_object(StockCountTemplate, 'id', value)
            if field == 'product':
                value = get_model_object(Product, 'id', value)
            if field == 'variance_reason' and value == 'Others':
                value = kwargs.get('specify_reason')
            if field is not None:
                setattr(stock_count, field, value)


validate_stock = ValidateStockCount()
