#
# Write a script to identify stale products
# From information in the sale performance table
#
import datetime
import csv

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import Max
from django.db.models import Q
from django.core.management.base import BaseCommand

from healthid.apps.sales.models import SalesPerformance
from healthid.apps.products.models import Product


class Command(BaseCommand):

    help = "A helper function to help identify stale products"

    def add_arguments(self, parser):
        # take in one optional argument, which is the period in months
        parser.add_argument("--months", type=int)

    def _write_to_csv(self, stale_products, stale_products_last_sale):
        # write the products to a csv
        todays_date = datetime.datetime.now()
        filename = f"/tmp/stale_products_{todays_date}.csv"
        with open(filename, mode="w") as csv_file:
            fieldnames = [
                "product_id",
                "product_name",
                "quantity_in_stock",
                "prefered_supplier",
                "backup_supplier",
                "last_sale",
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for stale_product in stale_products:
                writer.writerow(
                    {
                        "product_id": stale_product.id,
                        "product_name": stale_product.product_name,
                        "quantity_in_stock": stale_product.quantity_in_stock,
                        "prefered_supplier": stale_product.preferred_supplier,
                        "backup_supplier": stale_product.backup_supplier,
                        "last_sale": stale_products_last_sale.get(stale_product.id),
                    }
                )

    def _identify_stale_products(self, period_in_months):
        tolerance_date = timezone.now() - relativedelta(months=period_in_months)
        # get the most recent sale date for each product
        # and filter for the ones where the last sale occured before 'x' months ago which are stale
        product_most_recent_sale = (
            SalesPerformance.objects.values("product_id")
            .annotate(Max("transaction_date"))
            .filter(transaction_date__max__lt=tolerance_date)
        )
        stale_product_ids = product_most_recent_sale.values_list(
            "product_id", flat=True
        )

        # get all the products which have never been sold before, are not in the sale performance table
        distinct_product_ids = SalesPerformance.objects.values_list(
            "product_id", flat=True
        ).distinct()
        unsold_products = Product.objects.exclude(id__in=distinct_product_ids)

        # get the last sale date for each product
        stale_products_last_sale = {
            sale["product_id"]: sale["transaction_date__max"]
            for sale in product_most_recent_sale
        }

        stale_products = Product.objects.filter(
            Q(id__in=stale_product_ids) | Q(id__in=unsold_products)
        )
        self._write_to_csv(stale_products, stale_products_last_sale)

    def handle(self, *args, **options):
        default_period = 3
        period_in_months = options.get("months") or default_period
        self._identify_stale_products(period_in_months)
