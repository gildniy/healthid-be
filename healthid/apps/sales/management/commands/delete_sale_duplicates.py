# 
# Write a script to populate the sale performnce table
# From rows in the sales and saleDetails table
# 
from django.core.management.base import BaseCommand
from healthid.apps.sales.models import  Sale, SaleDetail


class Command(BaseCommand):
    args = 'No Arguments'
    help = 'A helper function to help populate the Sales performance Table'

    def _delete_sale_duplicates(self):
        # duplicate sales are not present in the saleDetail table
        total_deleted = 0
        all_sales = Sale.objects.all()
        print(f"The total sales are {len(all_sales)}")
        for single_sale in all_sales:
            corresponding_sale_detail = SaleDetail.objects.filter(
                sale_id = single_sale.id
            )
            
            if not corresponding_sale_detail:
                total_deleted+=1
                print(f"the sale id is {single_sale.id}")
                single_sale.delete()
        print(f"the total deleted items are {total_deleted}")
    def handle(self, *args, **options):
        self._delete_sale_duplicates()
