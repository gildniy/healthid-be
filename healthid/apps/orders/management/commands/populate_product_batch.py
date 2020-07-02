# 
# Write a script to populate the sale performnce table
# From rows in the sales and saleDetails table
# 
import datetime
from django.core.management.base import BaseCommand
from healthid.apps.orders.models.orders import ProductBatch, Order
from healthid.apps.products.models import BatchInfo, Quantity
from healthid.apps.authentication.models import User
from healthid.apps.business.models import Business
# from healthid.apps.outlets.models import Outlet

class Command(BaseCommand):
    args = 'No Arguments'
    help = 'A helper function to help populate the Product Batch Table'

    def _populate_product_batch_db(self):
        # get all the foriegnKeys and details required to create a new order
        order_name = "Pre Launch Order"
        order_user = User.objects.first()
        order_business = Business.objects.first()
        todays_date = datetime.date.today()
        # create a new order and save
        gotten_order, created_order = Order.objects.get_or_create(
            name = order_name,
            user_id = order_user.id,
            business_id = order_business.id,
            delivery_date = str(todays_date)
        )
        new_order = gotten_order or created_order

        
        # get all the current batchInfos
        for batch in BatchInfo.objects.all():
            new_product_batch = ProductBatch()
            batch_id = batch.id

            # get the corresponding quantity
            try:
                batch_quantity = Quantity.objects.get(batch_id = batch_id)
                new_batch_quantity = batch_quantity.quantity_received
            except:
                new_batch_quantity = 0

            new_product_batch.order_id = new_order.id

            new_product_batch.quantity = new_batch_quantity
            new_product_batch.supplier_id = batch.supplier_id
            new_product_batch.product_id = batch.product_id
            new_product_batch.batch_ref = batch.batch_no 
            new_product_batch.date_received = batch.date_received
            new_product_batch.expiry_date = batch.expiry_date
            new_product_batch.unit_cost = batch.unit_cost

            if new_product_batch.expiry_date > todays_date:
                new_product_batch.status = "EXPIRED"
            
            if new_product_batch.quantity == 0:
                new_product_batch.status = "OUT_OF_STOCK"

            new_product_batch.save()

    def handle(self, *args, **options):
        self._populate_product_batch_db()
