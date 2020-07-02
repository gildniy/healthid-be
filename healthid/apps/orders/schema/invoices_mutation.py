import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType
import cloudinary
import cloudinary.api
import cloudinary.uploader
from graphql_jwt.decorators import login_required
from healthid.apps.orders.models import Order, SupplierOrderDetails
from healthid.apps.orders.models.invoices import Invoice
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.validators import validate_empty_field
from healthid.utils.messages.orders_responses import\
    ORDERS_ERROR_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet


class InvoiceType(DjangoObjectType):
    class Meta:
        model = Invoice


class UploadInvoice(graphene.Mutation):
    """
    Uploads a new invoice for an order

    Args:
        id (int) order invoice id
        supplier_order_id (int) id of the order
        outlet_id (int) id of the outlet
        image_url (str) Invoice file to be uploaded
     returns:
        success message and details of the order and outlet
        otherwise GraphqlError instances are raised
    """
    invoice = graphene.Field(InvoiceType)
    message = graphene.String()

    class Arguments:
        supplier_order_id = graphene.String(required=True)
        invoice_file = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        supplier_order_id = kwargs.get('supplier_order_id')
        order = get_model_object(SupplierOrderDetails, 'id', supplier_order_id)
        destination_outlet = get_model_object(Order, 'id', order.order_id)
        invoice_document = kwargs.get('invoice_file')
        validate_empty_field('Invoice file', invoice_document)

        invoice_exist = \
            Invoice.objects.filter(order_id=supplier_order_id).exists()

        if invoice_exist:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES["duplicate_upload_error"])

        # check if order belongs to an outlet
        if destination_outlet.destination_outlet_id != outlet.id:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES["initiation_invoice_upload_error"])

        image_url = cloudinary.uploader.upload(invoice_document).get('url')

        invoice = Invoice(order_id=order.id, outlet_id=outlet.id,
                          image_url=image_url)

        with SaveContextManager(invoice) as invoice:
            return UploadInvoice(
                invoice=invoice,
                message=SUCCESS_RESPONSES["upload_success"].format("Invoice")
            )


class Mutation(graphene.ObjectType):
    upload_invoice = UploadInvoice.Field()
