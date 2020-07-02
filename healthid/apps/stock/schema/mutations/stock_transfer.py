import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.business.models import Business
from healthid.apps.orders.models.orders import ProductBatch, Order
from healthid.apps.orders.schema.order_query import ProductBatchType
from healthid.apps.outlets.models import Outlet
from healthid.apps.stock.models import StockTransfer, STARTED, TransferBatch, IN_TRANSIT, RECEIVED, SEND
from healthid.apps.stock.schema.types import StockTransferType, TransferBatchType
from healthid.utils.app_utils.database import get_model_object, SaveContextManager
from healthid.utils.messages.stock_responses import \
    STOCK_ERROR_RESPONSES, STOCK_SUCCESS_RESPONSES
import datetime

from healthid.utils.stock_utils.stock_transfer import StockTransferService, StockTransferValidator


class CreateStockTransfer(graphene.Mutation):
    """
    Mutation to a create new stock transfer

    args:
        business_id: ID of the business where the stock transfer is happening
        source_outlet_id: ID of the outlet from which stocks are originating
        destination_outlet_id: ID of the outlet that needs more stocks

    returns:
        success(str): success message confirming stock transfer initiation
        stock_transfer(obj): 'StockTransfer' object containing the
                          stock transfer details
    """

    success = graphene.Field(graphene.String)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)
    stock_transfer = graphene.Field(StockTransferType)

    class Arguments:
        business_id = graphene.String(required=True)
        source_outlet_id = graphene.String(required=True)
        destination_outlet_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        business_id = kwargs.get('business_id')
        source_outlet_id = kwargs.get('source_outlet_id')
        destination_outlet_id = kwargs.get('destination_outlet_id')
        business = get_model_object(Business, 'id', business_id)
        source_outlet = get_model_object(Outlet, 'id', source_outlet_id)
        destination_outlet = get_model_object(Outlet, 'id', destination_outlet_id)
        if source_outlet_id == destination_outlet_id:
            raise GraphQLError(STOCK_ERROR_RESPONSES["same_origin_stock_transfer"])
        elif not source_outlet.business.id == business_id or not destination_outlet.business.id == business_id:
            raise GraphQLError(STOCK_ERROR_RESPONSES["outlet_not_in_business"])
        stock_transfer = StockTransfer(
            business=business,
            source=source_outlet,
            destination=destination_outlet,
            initiated_by=user,
            status=STARTED,
            date_dispatched=datetime.date.today()
        )
        with SaveContextManager(stock_transfer) as stock_transfer:
            message = [STOCK_SUCCESS_RESPONSES["stock_transfer_open_success"]]
        return CreateStockTransfer(message=message, stock_transfer=stock_transfer)


class EditStockTransfer(graphene.Mutation):
    """
    Mutation to a update an existing stock transfer

    args:
        stock_transfer_id: ID of the stock transfer
        destination_outlet_id: ID of the outlet that needs more stocks

    returns:
        success(str): success message confirming stock transfer initiation
        stock_transfer(obj): 'StockTransfer' object containing the
                          stock transfer details
    """

    success = graphene.Field(graphene.String)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)
    stock_transfer = graphene.Field(StockTransferType)

    class Arguments:
        stock_transfer_id = graphene.String(required=True)
        destination_outlet_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        # initiation
        destination_outlet_id = kwargs.get('destination_outlet_id')
        stock_transfer = get_model_object(StockTransfer, 'id', kwargs.get('stock_transfer_id'))
        destination_outlet = get_model_object(Outlet, 'id', destination_outlet_id)

        # fluent validation
        StockTransferValidator(stock_transfer, info.context.user) \
            .allowed_when_stock_transfer_status() \
            .avoid_same_outlet_stock_transfer(destination_outlet) \
            .ensure_user_business_matches_stock_business() \
            .ensure_destination_outlet_is_within_business(destination_outlet)

        # mutation
        stock_transfer.destination = destination_outlet
        stock_transfer.save()
        message = [STOCK_SUCCESS_RESPONSES["stock_transfer_updated_success"]]
        return EditStockTransfer(message=message, stock_transfer=stock_transfer)


class SendOrQueryStockTransfer(graphene.Mutation):
    """
    Mutation to delete stock transfer business

    args:
        stock_transfer_id: ID of the of the stock transfer to delete

    returns:
        success(str): success message confirming stock deletion
        stock_transfer(obj): 'StockTransfer' object containing the
                          stock transfer details
    """
    stock_transfer = graphene.Field(StockTransferType)
    product_batches = graphene.List(ProductBatchType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    class Arguments:
        stock_transfer_id = graphene.String(required=True)
        action_type = graphene.String(required=True)

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        # initiation
        action_type = kwargs.get('action_type')
        stock_transfer = get_model_object(StockTransfer, 'id', kwargs.get('stock_transfer_id'))

        #  validations
        StockTransferValidator(stock_transfer, info.context.user) \
            .ensure_user_business_matches_stock_business() \
            .avoid_consecutive_stock_sending_or_querying(action_type)

        # mutation
        updated_product_batches, errors = StockTransferService.send_or_query_product_batches(
                                                    stock_transfer.transfer_batches, action_type)
        if not len(errors):
            product_batches = [product_batch.save() or product_batch for product_batch in updated_product_batches]
            stock_transfer.status = IN_TRANSIT if action_type == SEND else STARTED
            stock_transfer.save()
            message = "Stock transfer sent successfully"
        else:
            message = "Stock transfer failed"
            product_batches = []
        return SendOrQueryStockTransfer(message=message, errors=errors,
                                        stock_transfer=stock_transfer, product_batches=product_batches)


class ApproveStockTransfer(graphene.Mutation):
    """
    Mutation to delete stock transfer business

    args:
        stock_transfer_id: ID of the of the stock transfer to delete

    returns:
        success(str): success message confirming stock deletion
        stock_transfer(obj): 'StockTransfer' object containing the
                          stock transfer details
    """
    stock_transfer = graphene.Field(StockTransferType)
    errors = graphene.List(graphene.String)
    message = graphene.String()

    class Arguments:
        stock_transfer_id = graphene.String(required=True)

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        stock_transfer_id = kwargs.get('stock_transfer_id')
        stock_transfer = get_model_object(StockTransfer, 'id', stock_transfer_id)
        #  validations
        StockTransferValidator(stock_transfer, info.context.user) \
            .allowed_when_stock_transfer_status(only=IN_TRANSIT) \
            .ensure_user_business_matches_stock_business() \
            .ensure_stock_transfer_destination_outlet_matches_user_default_outlet()\
            .ensure_stock_transfer_has_transfer_batches()

        message, errors = StockTransferService.approve_transfer_batches(stock_transfer)

        return ApproveStockTransfer(message=message, stock_transfer=stock_transfer, errors=errors)


class DeleteStockTransfer(graphene.Mutation):
    """
    Mutation to delete stock transfer business

    args:
        stock_transfer_id: ID of the of the stock transfer to delete

    returns:
        success(str): success message confirming stock deletion
        stock_transfer(obj): 'StockTransfer' object containing the
                          stock transfer details
    """
    stock_transfer = graphene.Field(StockTransferType)

    class Arguments:
        stock_transfer_id = graphene.Int(required=True)

    errors = graphene.List(graphene.String)
    message = graphene.String()

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        user = info.context.user
        stock_transfer_id = kwargs.get('stock_transfer_id')
        stock_transfer = get_model_object(StockTransfer, 'id', stock_transfer_id)

        StockTransferValidator(stock_transfer, info.context.user) \
            .allowed_when_stock_transfer_status(only=STARTED) \
            .ensure_user_business_matches_stock_business() \
            .ensure_stock_transfer_source_outlet_matches_user_default_outlet()

        # do all the stock reversal or stock release procedures here
        message = STOCK_SUCCESS_RESPONSES[
            "stock_transfer_delete_success"].format(stock_transfer.id)
        stock_transfer.delete(user)
        return DeleteStockTransfer(message=message)


class AddTransferBatch(graphene.Mutation):
    """
    Mutation to add transfer batch.

    args:
        stock_transfer_id(int): id of the stock transfer to be edited
        product_ids(list): list of product ids

    returns:
        success(str): success message confirming transfer batch addition
        transfer_batch(obj): 'TransferBatch' object containing the
                             newly added transfer batch details
    """

    transfer_batch = graphene.Field(TransferBatchType)
    product_id = graphene.String()
    stock_transfer_id = graphene.String()
    success = graphene.String()
    message = graphene.String()

    class Arguments:
        stock_transfer_id = graphene.String(required=True)
        product_batch_id = graphene.String(required=True)
        destination_outlet_id = graphene.String(required=True)
        quantity_sent = graphene.String(required=True)
        comments = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        # initiation
        quantity_sent = float(kwargs["quantity_sent"])
        comments = kwargs["comments"]
        stock_transfer = get_model_object(StockTransfer, 'id', kwargs["stock_transfer_id"])
        product_batch = get_model_object(ProductBatch, 'id', kwargs["product_batch_id"])

        #  validations
        StockTransferValidator(stock_transfer, info.context.user) \
            .allowed_when_stock_transfer_status() \
            .ensure_user_business_matches_stock_business() \
            .ensure_stock_transfer_source_outlet_matches_user_default_outlet() \
            .ensure_quantity_sent_is_greater_than_1(quantity_sent)
        StockTransferValidator.ensure_quantity_sent_is_le_product_batch_quantity(product_batch, quantity_sent)

        # mutation
        transfer_batch = TransferBatch(
            stock_transfer=stock_transfer,
            product=product_batch.product,
            product_batch=product_batch,
            unit_cost=product_batch.unit_cost,
            quantity_sent=quantity_sent,
            expiry_date=product_batch.expiry_date,
            comments=comments
        )
        with SaveContextManager(transfer_batch) as transfer_batch:
            message = [STOCK_SUCCESS_RESPONSES["stock_transfer_batch_success"]]

        return AddTransferBatch(
            success='', transfer_batch=transfer_batch, message=message)


class EditTransferBatch(graphene.Mutation):
    """
    Mutation to add transfer batch.

    args:
        stock_transfer_id(int): id of the stock transfer to be edited
        product_ids(list): list of product ids

    returns:
        success(str): success message confirming transfer batch addition
        transfer_batch(obj): 'TransferBatch' object containing the
                             newly added transfer batch details
    """

    transfer_batch = graphene.Field(TransferBatchType)
    success = graphene.String()
    message = graphene.String()

    class Arguments:
        transfer_batch_id = graphene.String(required=True)
        quantity_sent = graphene.String(required=True)
        comments = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        transfer_batch = get_model_object(TransferBatch, 'id', kwargs["transfer_batch_id"])
        product_batch = transfer_batch.product_batch
        quantity_sent = float(kwargs["quantity_sent"])

        #  validations
        StockTransferValidator(transfer_batch.stock_transfer, info.context.user) \
            .allowed_when_stock_transfer_status() \
            .ensure_user_business_matches_stock_business() \
            .ensure_stock_transfer_source_outlet_matches_user_default_outlet() \
            .ensure_quantity_sent_is_greater_than_1(quantity_sent)
        StockTransferValidator.ensure_quantity_sent_is_le_product_batch_quantity(product_batch, quantity_sent)

        if not transfer_batch:
            raise GraphQLError(STOCK_ERROR_RESPONSES["transfer_batch_inexistent"])
        transfer_batch.quantity_sent = quantity_sent
        transfer_batch.comments = kwargs["comments"]
        transfer_batch.save()
        return EditTransferBatch(
            success='', transfer_batch=transfer_batch,
            message=STOCK_SUCCESS_RESPONSES["stock_transfer_batch_updated_success"])


class DeleteTransferBatch(graphene.Mutation):
    """
    Mutation to delete transfer batch from a stock transfer

    args:
        transfer_batch_id: ID of the of the transfer batch to delete

    returns:
        success(str): success message confirming transfer batch deletion
        transfer_batch(obj): 'TransferBatch' object containing the
                          transfer batch details
    """
    transfer_batch = graphene.Field(TransferBatchType)
    success = graphene.String()
    message = graphene.String()

    class Arguments:
        transfer_batch_id = graphene.String(required=True)

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        transfer_batch = get_model_object(TransferBatch, 'id', kwargs["transfer_batch_id"])
        if not transfer_batch:
            raise GraphQLError(STOCK_ERROR_RESPONSES["transfer_batch_inexistent"])

        #  validations
        StockTransferValidator(transfer_batch.stock_transfer, info.context.user) \
            .allowed_when_stock_transfer_status() \
            .ensure_user_business_matches_stock_business() \
            .ensure_stock_transfer_source_outlet_matches_user_default_outlet()

        transfer_batch.delete()
        return DeleteTransferBatch(
            success='', transfer_batch=transfer_batch,
            message=STOCK_SUCCESS_RESPONSES["stock_transfer_batch_deleted"])


class DeleteTransferBatches(graphene.Mutation):
    """
    Mutation to delete transfer batch from a stock transfer

    args:
        transfer_batch_id: ID of the of the transfer batch to delete

    returns:
        success(str): success message confirming transfer batch deletion
        transfer_batch(obj): 'TransferBatch' object containing the
                          transfer batch details
    """
    transfer_batches = graphene.List(TransferBatchType)
    success = graphene.String()
    message = graphene.String()

    class Arguments:
        stock_transfer_id = graphene.String(required=True)
        product_ids = graphene.List(graphene.String)

    @staticmethod
    @login_required
    def mutate(root, info, **kwargs):
        stock_transfer_id = kwargs["stock_transfer_id"]
        product_ids = kwargs["product_ids"]
        deleted_transfer_batches = []
        stock_transfer = get_model_object(StockTransfer, 'id', stock_transfer_id)

        if not len(product_ids):
            raise GraphQLError("Missing array of product_ids")

        #  validations
        StockTransferValidator(stock_transfer, info.context.user) \
            .allowed_when_stock_transfer_status() \
            .ensure_user_business_matches_stock_business() \
            .ensure_stock_transfer_source_outlet_matches_user_default_outlet()

        for product_id in product_ids:
            stock_transfer_batches = TransferBatch.objects.filter(product_id=product_id,
                                                                  stock_transfer_id=stock_transfer_id)
            if stock_transfer_batches:
                for stock_transfer_batch in stock_transfer_batches:
                    deleted_transfer_batches.append(stock_transfer_batch)
                    stock_transfer_batch.delete()

        return DeleteTransferBatches(
            success='', transfer_batches=deleted_transfer_batches,
            message=STOCK_SUCCESS_RESPONSES["stock_transfer_batches_deleted"])
