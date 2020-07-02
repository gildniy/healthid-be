from rest_framework.exceptions import ValidationError


def check_product_category(user_bussinesses, product_categories,
                           searched_category, row_count):
    product_category = None
    for user_business in user_bussinesses:
        for category in product_categories:
            if category.get('business_id') == user_business.get('id'):
                product_category = category
                break
        if product_category:
            break
    if not product_category:
        raise ValidationError({
            'error': "This category '{}' does not exist on row {}"
            .format(searched_category, row_count)
        })
    return product_category
