from rest_framework.exceptions import ValidationError


def check_product(user_bussinesses, products,
                  searched_product, row_count,
                  ignore=False):
    found_product = None
    for user_business in user_bussinesses:
        for product in products:
            if product.get('business_id') == user_business.get('id'):
                found_product = product
                break
        if found_product:
            break
    if not found_product and not ignore:
        raise ValidationError({
            'error': "This product '{}' does not exist on row {}"
            .format(searched_product, row_count)
        })
    return found_product
