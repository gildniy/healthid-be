from graphql import GraphQLError
from django.db.models import Q, Sum
from healthid.apps.orders.models.orders import ProductBatch
from healthid.apps.stock.models import RECEIVED, TransferBatch, STARTED, IN_TRANSIT, SEND, QUERY
import datetime

from healthid.apps.stock.schema.types import StockTransferAggregateType
from healthid.utils.app_utils.check_user_in_outlet import check_user_has_an_active_outlet
from healthid.utils.messages.stock_responses import STOCK_ERROR_RESPONSES


class StockTransferService:
    @staticmethod
    def aggregate_transfer_batches(stock_transfer):
        aggregate_dict = dict()
        product_batch_ids = list()
        for transfer_batch in stock_transfer.transfer_batches:
            product = transfer_batch.product
            product_batch = transfer_batch.product_batch
            product_batch_ids.append(product_batch.id)
            if not aggregate_dict.get(product.sku_number):
                aggregate_dict[product.sku_number] = StockTransferAggregateType(
                    product_name=product.product_name,
                    product_sku_number=product.sku_number,
                    quantity_in_batches=product_batch.quantity,
                    quantity_sent=transfer_batch.quantity_sent,
                    batches=1
                )
            else:
                stock_transfer_aggregate = aggregate_dict[product.sku_number]
                stock_transfer_aggregate.quantity_sent += transfer_batch.quantity_sent
                aggregate_dict[product.sku_number].quantity_in_batches += \
                    0 if product_batch_ids.count(product_batch.id) > 1 else product_batch.quantity
                stock_transfer_aggregate.batches += 1
            return aggregate_dict

    @staticmethod
    def send_or_query_product_batches(transfer_batches, action_type):
        updated_product_batches = []
        errors = []
        for transfer_batch in transfer_batches:
            product_batch = transfer_batch.product_batch
            if action_type == SEND and product_batch.quantity < transfer_batch.quantity_sent:
                product = transfer_batch.product
                errors.append(f'Error supplying {transfer_batch.quantity_sent}'
                              f' of {product.product_name},'
                              f' {product_batch.quantity} available')
            else:
                if action_type == SEND:
                    product_batch.quantity -= transfer_batch.quantity_sent
                elif action_type == QUERY:
                    product_batch.quantity += transfer_batch.quantity_sent
                updated_product_batches.append(product_batch)
        return updated_product_batches, errors

    @staticmethod
    def approve_transfer_batches(stock_transfer):
        todays_date = datetime.date.today()
        for transfer_batch in stock_transfer.transfer_batches:
            old_product_batch = transfer_batch.product_batch
            new_product_batch = ProductBatch()
            new_product_batch.quantity = transfer_batch.quantity_sent
            new_product_batch.order_id = old_product_batch.order_id
            new_product_batch.outlet_id = stock_transfer.destination.id

            new_product_batch.supplier_id = old_product_batch.supplier_id
            new_product_batch.product_id = old_product_batch.product_id
            new_product_batch.batch_ref = old_product_batch.batch_ref
            new_product_batch.date_received = todays_date
            new_product_batch.expiry_date = old_product_batch.expiry_date
            new_product_batch.unit_cost = old_product_batch.unit_cost

            if new_product_batch.expiry_date > todays_date:
                new_product_batch.status = "EXPIRED"

            if new_product_batch.quantity == 0:
                new_product_batch.status = "OUT_OF_STOCK"

            new_product_batch.save()
            transfer_batch.quantity_received = transfer_batch.quantity_sent
            transfer_batch.save()
        stock_transfer.status = RECEIVED
        stock_transfer.save()
        message = 'Successfully approved stock transfer '
        errors = []
        return message, errors


class StockTransferValidator:
    def __init__(self, stock_transfer, user):
        self.stock_transfer = stock_transfer
        self.user = user
        self.default_outlet = check_user_has_an_active_outlet(user)
        self.user_business = user.business_user

    def allowed_when_stock_transfer_status(self, only=STARTED):
        if not self.stock_transfer.status == only:
            raise GraphQLError(f"Cannot modify stock transfer when {self.stock_transfer.status}")
        return self

    def avoid_same_outlet_stock_transfer(self, destination_outlet):
        if self.stock_transfer.source == destination_outlet:
            raise GraphQLError(STOCK_ERROR_RESPONSES["same_origin_stock_transfer"])
        return self

    def ensure_destination_outlet_is_within_business(self, destination_outlet):
        business = self.stock_transfer.business
        if not destination_outlet.business.id == business.id:
            raise GraphQLError(STOCK_ERROR_RESPONSES["outlet_not_in_business"])
        return self

    def ensure_user_business_matches_stock_business(self):
        business = self.stock_transfer.business
        if not business == self.user_business:
            raise GraphQLError("User not in stock transfer business")
        return self

    def avoid_consecutive_stock_sending_or_querying(self, action_type):
        stock_transfer = self.stock_transfer
        default_outlet = self.default_outlet
        if action_type == SEND:
            if not default_outlet == stock_transfer.source:
                raise GraphQLError("User not in stock transfer source outlet")
            if not stock_transfer.status == STARTED:
                raise GraphQLError("Stock transfer already sent")
        elif action_type == QUERY:
            if not default_outlet == stock_transfer.destination:
                raise GraphQLError("User not in stock transfer destination outlet")
            if not stock_transfer.status == IN_TRANSIT:
                raise GraphQLError("Please wait for the sending outlet to send the product batches")
        else:
            raise GraphQLError(f"Invalid action type. Use SEND or QUERY")
        return self

    def ensure_stock_transfer_source_outlet_matches_user_default_outlet(self):
        if not self.stock_transfer.source == self.default_outlet:
            raise GraphQLError(STOCK_ERROR_RESPONSES["stock_transfer_not_for_outlet"])
        return self

    def ensure_stock_transfer_destination_outlet_matches_user_default_outlet(self):
        if not self.stock_transfer.destination == self.default_outlet:
            raise GraphQLError(STOCK_ERROR_RESPONSES["stock_transfer_not_for_outlet"])
        return self

    def ensure_stock_transfer_has_transfer_batches(self):
        if not len(self.stock_transfer.transfer_batches):
            raise GraphQLError("No stock transfer batches")
        return self

    @staticmethod
    def ensure_quantity_sent_is_le_product_batch_quantity(product_batch, quantity_sent):
        # we need to account for multiple quantity sent to all outlets, yet to be processed
        # so filtering with 0 quantity_received signifies in_transit stock transfers
        initial_quantities = TransferBatch.objects.filter(
            Q(product_batch=product_batch) &
            Q(quantity_received=0)).aggregate(Sum('quantity_sent'))
        if product_batch.quantity < (quantity_sent + initial_quantities.get('quantity_sent__sum')):
            raise GraphQLError(STOCK_ERROR_RESPONSES["not_enough_stock_transfer_quantity"].format(quantity_sent))

    @staticmethod
    def ensure_quantity_sent_is_greater_than_1(quantity_sent):
        if quantity_sent <= 0:
            raise GraphQLError(STOCK_ERROR_RESPONSES["minimum_stock_transfer_quantity"])

    @staticmethod
    def ensure_resource_exists(quantity_sent):
        if quantity_sent <= 0:
            raise GraphQLError(STOCK_ERROR_RESPONSES["minimum_stock_transfer_quantity"])
