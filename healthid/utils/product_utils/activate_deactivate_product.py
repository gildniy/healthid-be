from graphql import GraphQLError
from healthid.apps.products.models import Product


def activate_deactivate_products(product_ids, is_active, error_msg):
    if not product_ids:
        raise GraphQLError('Please provide product ids.')
    products = []
    for product_id in product_ids:
        try:
            product = Product.all_products.get(id=product_id,
                                               is_active=is_active)
        except Product.DoesNotExist:
            raise GraphQLError(error_msg.format(product_id=product_id))
        products.append(product)
    for product in products:
        product.is_active = not is_active
        product.save()
    return products
