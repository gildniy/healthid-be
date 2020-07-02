import graphene
from graphql_jwt.decorators import login_required
from healthid.apps.orders.schema.mutations.orders.mark_supplier_order_as_sent import MarkSupplierOrderAsSent
from healthid.apps.orders.schema.mutations.orders.send_supplier_order_emails import SendSupplierOrderEmails


class PlaceOrder(graphene.Mutation):
    """
    Send Supplier Order Emails to suppliers
    and 
    Mark Supplier Order Details as sent

    Args:
        supplier_order_ids: A list of supplier ids and  order ids 
        e.g [{
                orderId:orderId(Int)
                supplierId:supplierId(String)
            }]

    Returns:
        message: a return message
    """

    order_message = graphene.String()
    mail_message = graphene.String()

    class Arguments:
        supplier_order_ids = graphene.List(graphene.String, required=True)

    @login_required
    def mutate(self, info, **kwargs):
        supplier_order_ids = kwargs.get('supplier_order_ids')

        mark_order_as_sent = MarkSupplierOrderAsSent()
        send_supplier_order_emails = SendSupplierOrderEmails()

        # call the MarkSupplierOrderAsSent and SendSupplierOrderEmails methods
        order_message = mark_order_as_sent.mutate(info, supplier_order_ids = supplier_order_ids)
        mail_message = send_supplier_order_emails.mutate(info, supplier_order_ids = supplier_order_ids)

        return PlaceOrder(
                order_message = order_message.message, 
                mail_message = mail_message.message
                )
