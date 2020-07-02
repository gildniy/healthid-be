from healthid.apps.products.models import Product
from graphql import GraphQLError


class ProductQuery:

    def query_product_category(self, product_category_id):
        products = Product.objects.filter(
                product_category=product_category_id)
        if products.count() < 1:
            raise GraphQLError(
                    "The product with category Id {} does not exist"
                    .format(product_category_id))
        return products
