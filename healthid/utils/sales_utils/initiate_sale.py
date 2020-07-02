import math
from healthid.apps.products.models import Quantity
from healthid.apps.orders.models.orders import ProductBatch
from django.db.models import F


def initiate_sale(product_batch_instances, sold_products_instances, sale, sale_detail,
                  batch_history):
    """
    This function create a sale detail by looping through all sold
    products and create a record in SaleDetail by adding sale Id.

    It deduct sold quantity from batch quantity
    args:
        product_batch_instance : Holds a list of ProductBatch objects corresponding to the batch_id's 
        sold_products_instance : Holds a list of sold product
        sale: Holds a sale instance
        sale_detail: Holds sale detail model passed as argument
    """
    products = zip(product_batch_instances, sold_products_instances)
    sale_details = []
    sold_products_loyalty_points = []
    for product_batch_instance, sold_products_instance in products:
        product_category = product_batch_instance.product.product_category
        loyalty_points = (sold_products_instance.price / product_category.amount_paid) * product_batch_instance.product.loyalty_weight  # noqa
        sold_products_loyalty_points.append(math.floor(loyalty_points))

        # adjust the quantity sold to reflect in prodcut batches
        batch_product = ProductBatch.objects.get(
                id = product_batch_instance.id
            )
        if sale.return_sale_id:
            quantity_left = batch_product.quantity + sold_products_instance.quantity
            sold_products_instance.price *= -1
        else:
            quantity_left = batch_product.quantity - sold_products_instance.quantity

        if quantity_left < 0:
            raise ValueError(
                f'Error:Trying to sell more products than you have in stock.'
                )
        batch_product.quantity = quantity_left
        # if the quantity is less than 0, set the status to out_of_stock
        if batch_product.quantity == 0:
            batch_product.status = "OUT_OF_STOCK"
            batch_product.product.update_inventory()
        if sale.return_sale_id:
            batch_product.status = "IN_STOCK"
            batch_product.product.update_inventory()
        batch_product.save()

        detail = sale_detail(quantity=sold_products_instance.quantity,
                             discount=sold_products_instance.discount,
                             price=sold_products_instance.price,
                             note="",
                             batch_id=batch_product.id,
                             product=product_batch_instance.product,
                             sale=sale)
        sale_details.append(detail)

    sale_detail.objects.bulk_create(sale_details)
    return sum(sold_products_loyalty_points)
