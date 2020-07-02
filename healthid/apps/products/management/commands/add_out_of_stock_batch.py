# Write a script to set the out of stock batches of all existing products
# in the system.

from django.core.management.base import BaseCommand
from healthid.apps.products.models import BatchInfo, Product, Quantity
from healthid.apps.outlets.models import OutletUser
from django.utils import timezone
from healthid.utils.product_utils.product import addOutOfStockBatch
from dateutil import parser
from datetime import datetime
from healthid.apps.business.models import Business
from healthid.apps.authentication.models import User


class Command(BaseCommand):
    args = 'No arguments'
    help = 'add out of stock batch to all of the products in the system.'

    def _addOutOfStockBatch(self):
        products = Product.objects.filter(is_approved=True)
        business_ids = [product.business_id for product in products]
        businesses = Business.objects.filter(id__in=business_ids)

        # map owners to products that have businesses
        users_products = self._attach_products_with_business_to_their_owners(products, businesses)
        master_admin = User.objects.filter(role_id='adm000001').first().id
      

        products_batch_info = BatchInfo.objects.filter(batch_no='OUT OF STOCK')
        product_ids = [batch_info.product_id for batch_info in products_batch_info]


        batches_to_update = []
        for product in products:
            if product.id not in product_ids and product.business_id:
                batch_info = BatchInfo()
                batch_info.batch_no = 'OUT OF STOCK'
                batch_info.product = product
                batch_info.comment = ''
                batch_info.date_received = datetime.date(timezone.now())
                batch_info.delivery_promptness = True
                batch_info.expiry_date = datetime.date(
                    parser.parse('2099-01-01'))
                batch_info.supplier = product.preferred_supplier
                batch_info.unit_cost = product.sales_price or 0
                batch_info.user_id = self._get_owner_of_product(
                    product.id, users_products) or master_admin
                batches_to_update.append(batch_info)

                batch_info.save()
                self._addOutOfStockQuantity(batch_info)

        self._update_new_batches_number_to_out_of_stock(batches_to_update)

        
    def _addOutOfStockQuantity(self, batch_info, quantity=99):
        quantity = Quantity(
            batch=batch_info, quantity_received=quantity,
            quantity_remaining=quantity, is_approved=True)
        quantity.save()

    def _get_owner_of_product(self, passed_product_id, users_products):
        for product_id, user_id in users_products.items():
            if product_id == passed_product_id:
                return user_id

    def _attach_products_with_business_to_their_owners(self, products, businesses):
        users_products = {}
        for product in products:
          for business in businesses:
            if business.id == product.business_id:
              users_products[product.id] = business.user_id
        
        return users_products

    def _update_new_batches_number_to_out_of_stock(self, batches):
      for batch in batches:
          BatchInfo.objects.filter(id=batch.id).update(batch_no='OUT OF STOCK')

    def handle(self, *args, **options):
        self._addOutOfStockBatch()
