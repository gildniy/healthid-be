# 
# Write a script to identify stale products
# From information in the sale performance table
# 
from django.core.management.base import BaseCommand

from django.utils import timezone

from django.db.models.functions import ExtractWeek
from django.db.models import Sum
from dateutil.relativedelta import relativedelta


from healthid.apps.products.models import Product, ProductMeta
from healthid.apps.sales.models import SaleDetail


class Command(BaseCommand):

    help = 'A helper function to help update the sale velocity'

    def _update_sale_velocity(self, velocity_dict):
        """
        recieves the calculated sale velocity and updates the product meta with it
        """
        for product_id, sale_velocity in velocity_dict.items():
            product_meta, _ = ProductMeta.objects.get_or_create(
                dataKey = "Sale Velocity",
                product_id = product_id
            )
            product_meta.dataValue = sale_velocity
            product_meta.save()

    def _calculate_sale_velocity(self):
        """
        for each product present in the sale detail table
        calculate the sale velocity and store it
        """
        maximum_weeks = 4
        four_weeks_ago = timezone.now() - relativedelta(weeks = maximum_weeks)
        velocity_dict = {}

        #get sales from at most 4 weeks ago
        sale_details = SaleDetail.objects.filter(created_at__gt = four_weeks_ago)
        # get the sum of quantity grouped by week and product_id
        product_and_week_sale = sale_details.annotate(week  = ExtractWeek('created_at')).values('product_id','week').annotate(weekly_quantity = Sum("quantity"))
        # get all the distinct product id's present
        distinct_product_ids = product_and_week_sale.values_list('product_id', flat=True).distinct()
        # for each product calculate the sale velocity
        for product_id in distinct_product_ids:
            weekly_sales = product_and_week_sale.filter(product_id = product_id).values_list('weekly_quantity',flat= True)
            sale_velocity = sum(weekly_sales)/len(weekly_sales)
            velocity_dict[product_id] = sale_velocity

        self._update_sale_velocity(velocity_dict)

    def handle(self, *args, **options):
        self._calculate_sale_velocity()
