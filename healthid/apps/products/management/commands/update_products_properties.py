# 
# Write a script to set the outlet_id of all existing batches 
# to the assigned outlet of the user who created them.
# 
from django.core.management.base import BaseCommand
from healthid.apps.products.models import Product

class Command(BaseCommand):
    args = 'No Arguments'
    help = 'A helper function to help populate the BatchInfo outlet_id to that of the user who created it'

    def _update_product_properties(self):
        # get all products and update the properties on them
        all_products = Product.objects.all()
        for product in all_products:
            product.update_quantity_in_stock()
            product.update_autofill_quantity()
            product.update_avarage_unit_cost()
            product.update_pre_tax_retail_price()


    def handle(self, *args, **options):
        self._update_product_properties()
