from django.db.utils import DatabaseError, OperationalError

from healthid.apps.products.models import Product


class SetPrice:
    """This class handles setting prices to a group
    of products
    """

    def __init__(self):
        self.errors = []
        self.products = []

    def update_product_price(self, product, **kwargs):
        if kwargs.get('sales_price'):
            product.sales_price = kwargs.get('sales_price')
            product.auto_price = False
        else:
            product.markup = kwargs.get('markup')
            product.auto_price = True
        Product.pre_tax_retail_price_calculator(product)
        product.save()
        self.products.append(product)
        return (self.errors, self.products)
