import graphene

from healthid.apps.orders.schema.mutations.orders.initiate_order \
    import InitiateOrder
from healthid.apps.orders.schema.mutations.orders.edit_initiated_order \
    import EditInitiateOrder, EditProductsOrderItem, DeleteProductsOrderItem, ManualAddingProduct, ManualAddingSupplier
from healthid.apps.orders.schema.mutations.orders.add_order_details \
    import AddOrderDetails
from healthid.apps.orders.schema.mutations.orders.add_order_notes \
    import AddOrderNotes
from healthid.apps.orders.schema.mutations.orders.approve_supplier_order \
    import ApproveSupplierOrder
from healthid.apps.orders.schema.mutations.orders.\
    mark_supplier_order_status_approved \
    import ChangeSupplierOrderStatus
from healthid.apps.orders.schema.mutations.orders.send_supplier_order_emails \
    import SendSupplierOrderEmails
from healthid.apps.orders.schema.mutations.orders.mark_supplier_order_as_sent \
    import MarkSupplierOrderAsSent
from healthid.apps.orders.schema.mutations.orders.delete_order_detail \
    import DeleteOrderDetail
from healthid.apps.orders.schema.mutations.orders.close_order \
    import CloseOrder
from healthid.apps.orders.schema.mutations.orders.cancel_order \
    import CancelOrder
from healthid.apps.orders.schema.mutations.orders.place_order_mutation \
    import PlaceOrder
from healthid.apps.orders.schema.mutations.orders.product_batches \
    import CreateProductBatch, updateProductBatch, deleteProductBatch
from healthid.apps.orders.schema.mutations.orders.supplier_order \
    import CreateSupplierOrder, UpdateSupplierOrder, DeleteSupplierOrder, GenerateOrder, SupplierOrderRecieved


class Mutation(graphene.ObjectType):
    initiate_order = InitiateOrder.Field()
    edit_initiated_order = EditInitiateOrder.Field()
    add_order_items = ManualAddingProduct.Field()
    update_order_items = updateProductBatch.Field()
    delete_products_order_item = DeleteProductsOrderItem.Field()
    edit_products_order_item = EditProductsOrderItem.Field()
    add_order_details = AddOrderDetails.Field()
    add_order_notes = AddOrderNotes.Field()
    approve_supplier_order = ApproveSupplierOrder.Field()
    mark_supplier_order_status_approved = ChangeSupplierOrderStatus.Field()
    send_supplier_order_emails = SendSupplierOrderEmails.Field()
    mark_supplier_order_as_sent = MarkSupplierOrderAsSent.Field()
    delete_order_detail = DeleteOrderDetail.Field()
    cancel_order = CancelOrder.Field()
    close_order = CloseOrder.Field()
    create_product_batch = CreateProductBatch.Field()
    update_product_batch = updateProductBatch.Field()
    delete_product_batch = deleteProductBatch.Field()
    place_order = PlaceOrder.Field()
    create_supplier_order = CreateSupplierOrder.Field()
    update_supplier_order = UpdateSupplierOrder.Field()
    delete_supplier_order = DeleteSupplierOrder.Field()
    generate_order = GenerateOrder.Field()
    mark_supplier_order_as_recieved = SupplierOrderRecieved.Field()
