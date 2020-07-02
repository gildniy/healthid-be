import graphene

from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import BarcodeScan

from healthid.utils.app_utils.database import SaveContextManager
from healthid.apps.orders.forms import BarcodeScanForm
from healthid.utils.messages.orders_responses import ORDERS_SUCCESS_RESPONSES


class BarcodeScanType(DjangoObjectType):

    class Meta:
        model = BarcodeScan


class RecordScan(graphene.Mutation):
    """Mutation to save a record of a barcode scan."""
    barcode_scan = graphene.Field(BarcodeScanType)
    message = graphene.String()

    class Arguments:
        scanned_number = graphene.String(required=True)
        batch_id = graphene.String(required=True)
        order_id = graphene.Int(required=True)
        outlet_id = graphene.Int(required=True)
        product_id = graphene.Int(required=True)
        count = graphene.Int(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        """Save the barcode scan information.

        Use the scanned_number, batch_id, order_id, product_id, outlet_id to
        query for matching BatchInfo, Order, Order, Product, Outlet instances
        respectively, to be linked to the BarcodeScan instance being created.
        This should only be done when the order is marked as closed.

        Args:
            scanned_number (str): The number scanned from the barcode
            batch_id (int): The id for the batch
            order_id (int): The id for the order
            outlet_id (int): The id for the business Outlet
            product_id (int): The id for the product

        Raises:
            GraphQLError: if order is not closed

        Returns:
            barcode_scan (:obj): Barcode scan dict
            message (str): success message
        """
        data = {
            'scanned_number': kwargs.get('scanned_number'),
            'order_id': kwargs.get('order_id'),
            'batch_id': kwargs.get('batch_id'),
            'count': kwargs.get('count'),
            'outlet_id': kwargs.get('outlet_id'),
            'product_id': kwargs.get('product_id'),
        }

        form = BarcodeScanForm(data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
        else:
            raise GraphQLError(form.errors)
        barcode_scan = BarcodeScan(
            scanned_number=cleaned_data['scanned_number'],
            order_id=cleaned_data['order_id'],
            batch_info_id=cleaned_data['batch_id'],
            count=cleaned_data['count'],
        )
        with SaveContextManager(barcode_scan) as barcode_scan:
            message = ORDERS_SUCCESS_RESPONSES["scan_save_success"]
            return RecordScan(barcode_scan=barcode_scan, message=message)


class Mutation(graphene.ObjectType):
    record_scan = RecordScan.Field()
