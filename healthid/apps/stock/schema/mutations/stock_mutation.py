import graphene

from healthid.apps.stock.schema.mutations.open_stock_transfer \
    import OpenStockTransfer
from healthid.apps.stock.schema.mutations.close_stock_transfer \
    import CloseStockTransfer

from healthid.apps.stock.schema.mutations.create_stock_count_template \
    import CreateStockCountTemplate
from healthid.apps.stock.schema.mutations.delete_stock_count_template \
    import DeleteStockCountTemplate
from healthid.apps.stock.schema.mutations.edit_stock_count_template \
    import EditStockCountTemplate

from healthid.apps.stock.schema.mutations.initiate_stock_count \
    import InitiateStockCount
from healthid.apps.stock.schema.mutations.update_stock_count \
    import UpdateStockCount
from healthid.apps.stock.schema.mutations.delete_stock_count \
    import DeleteStockCount

from healthid.apps.stock.schema.mutations.remove_batch_stock \
    import RemoveBatchStock

from healthid.apps.stock.schema.mutations.reconcile_stock \
    import ReconcileStock
from healthid.apps.stock.schema.mutations \
    import stock_transfer


class Mutation(graphene.ObjectType):
    initiate_stock = InitiateStockCount.Field()
    update_stock = UpdateStockCount.Field()
    delete_stock = DeleteStockCount.Field()
    remove_batch_stock = RemoveBatchStock.Field()
    reconcile_stock = ReconcileStock.Field()
    open_stock_transfer = OpenStockTransfer.Field()
    close_stock_transfer = CloseStockTransfer.Field()
    create_stock_count_template = CreateStockCountTemplate.Field()
    edit_stock_count_template = EditStockCountTemplate.Field()
    delete_stock_count_template = DeleteStockCountTemplate.Field()

    create_stock_transfer = stock_transfer.CreateStockTransfer.Field()
    edit_stock_transfer = stock_transfer.EditStockTransfer.Field()
    send_or_query_stock_transfer = stock_transfer.SendOrQueryStockTransfer.Field()
    approve_stock_transfer = stock_transfer.ApproveStockTransfer.Field()
    delete_stock_transfer = stock_transfer.DeleteStockTransfer.Field()
    add_stock_transfer_batch = stock_transfer.AddTransferBatch.Field()
    edit_stock_transfer_batch = stock_transfer.EditTransferBatch.Field()
    delete_stock_transfer_batch = stock_transfer.DeleteTransferBatch.Field()
    delete_stock_transfer_batches = stock_transfer.DeleteTransferBatches.Field()
