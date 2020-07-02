from datetime import timezone, datetime
from django.db.models import Q
from itertools import compress
from graphql import GraphQLError
from functools import reduce


from healthid.apps.preference.models import OutletPreference
from healthid.apps.products.models import Product, BatchInfo, Quantity
from healthid.apps.orders.models.orders import ProductBatch
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.query_objects import GetObjectList
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES


class SalesValidator:
    def __init__(self, batches):
        self.product_quantities = []
        self.product_discounts = []
        self.product_prices = []
        self.product_ids = []
        self.batch_ids = []
        for product in batches:
            self.product_quantities.append(product['quantity'])
            self.product_discounts.append(product.get('discount'))
            self.product_prices.append(product['price'])
            self.batch_ids.append(product['batch_id'])

        self.batch_queryset = self.get_batches()
        self.batches_db_ids = self.batch_queryset.values_list('id', flat=True)
        self.sorted_batch_queryset = sorted(
            self.batch_queryset, key=lambda x: self.batch_ids.index(x.id))

        self.batches_quantity = self.get_batches_quantity()
        self.sorted_batches_quantity = sorted(
            self.batches_quantity, key=lambda x: self.batch_ids.index(
                x.batch_id)
        )
        for batch in self.sorted_batch_queryset:
            self.product_ids.append(batch.product.id)

        self.product_queryset = self.get_products()
        self.products_db_ids = self.product_queryset.values_list(
            'id', flat=True)
        self.batches_db_quantity = [
            product.quantity_remaining
            for product in self.sorted_batches_quantity]

    def get_products(self):
        message = "Sale must have at least 1 product"
        product_queryset = GetObjectList.get_objects(
            Product, self.product_ids, message)
        return product_queryset

    def get_batches(self):
        message = "Sale must have at least 1 batch"
        batch_queryset = GetObjectList.get_objects(
            ProductBatch, self.batch_ids, message
        )
        return batch_queryset

    def get_batches_quantity(self):
        query = reduce(lambda q, id: q | Q(batch_id=id), self.batch_ids, Q())
        batch_queryset = Quantity.objects.filter(query)
        return batch_queryset

    def check_validity_of_ids(self):
        is_valid = [
            batch_id in self.batches_db_ids for batch_id in self.batch_ids
        ]

        if not all(is_valid):
            invalid_items = list(
                compress(self.batch_ids, [not item for item in is_valid]))
            message = 'Batches with ids {} do not exist'.format(
                ",".join(map(str, invalid_items)))
            raise GraphQLError(message)

    def check_validity_quantity_sold(self):
        message = SALES_ERROR_RESPONSES['less_quantities']  # noqa
        is_valid = [(existing_quantity >= requested_quantity) and
                    (requested_quantity > 0) for existing_quantity,
                    requested_quantity in
                    zip(self.batches_db_quantity, self.product_quantities)]
        if not all(is_valid):
            invalid_quantities = list(
                compress(self.batch_ids, [not item for item in is_valid]))

            message = message.format(",".join(map(str, invalid_quantities)))
            raise GraphQLError(message)

        return self.sorted_batch_queryset

    def check_product_price(self):
        message = SALES_ERROR_RESPONSES['negative_integer']
        is_valid = [price > 1 for price in self.product_prices]
        if not all(is_valid):
            invalid_quantities = list(
                compress(self.batch_ids, [not item for item in is_valid]))
            message = message.format(",".join(map(str, invalid_quantities)))
            raise GraphQLError(message)

    def check_product_discount(self):
        message = SALES_ERROR_RESPONSES['negative_discount']
        is_valid = [discount >= 0 and discount <=
                    100 for discount in self.product_discounts]
        if not all(is_valid):
            invalid_quantities = list(
                compress(self.batch_ids, [not item for item in is_valid]))
            message = message.format(",".join(map(str, invalid_quantities)))
            raise GraphQLError(message)

    def check_sales_fields_validity(self, **kwargs):
        discount_total = kwargs.get('discount_total')
        sub_total = kwargs.get('sub_total')
        amount_to_pay = kwargs.get('amount_to_pay')
        paid_amount = kwargs.get('paid_amount')
        change_due = kwargs.get('change_due')
        if discount_total < 0:
            raise GraphQLError(
                "Discount should not be less than 0")

        if amount_to_pay < 0 or sub_total < 1:
            raise GraphQLError(
                "Amount should be greater than 1")

        if change_due < 0:
            raise GraphQLError(
                "The Change due should not be less than 0")

        if paid_amount < 0:
            raise GraphQLError(
                "The paid amount should not be less than 0")

    def check_payment_method(self, **kwargs):
        payment_method = kwargs.get('payment_method').lower()
        outlet_id = kwargs.get('outlet_id')
        preferences = get_model_object(
            OutletPreference, 'outlet_id', outlet_id)
        message = SALES_ERROR_RESPONSES['invalid_payment']
        if preferences.payment_method == 'all' and \
                str.lower(payment_method) not in ['cash', 'card', 'credit', 'bank_transfer', 'split']:
            raise GraphQLError(message)

        if preferences.payment_method != 'all' and \
                str.lower(payment_method) not in ['others', 'credit', 'card', 'bank_transfer', 'split']:
            if preferences.payment_method != payment_method:
                raise GraphQLError(message)

    def check_product_returnable(self):
        message = message = SALES_ERROR_RESPONSES['not_returnable']
        is_valid = [product.is_returnable for product in self.product_queryset]
        if not all(is_valid):
            invalid_items = list(
                compress(self.product_ids, [not item for item in is_valid]))
            message = message.format(
                ",".join(map(str, invalid_items)))
            raise GraphQLError(message)

    def check_product_dates_for_return(self, outlet, sales_instance):
        message = "Product preferred returnable days are done"
        date_of_purchase = sales_instance.created_at
        date_difference = datetime.now(timezone.utc) - date_of_purchase
        date_change = date_difference.days
        if outlet.outletpreference.returnable_days < date_change:
            raise GraphQLError(message)
