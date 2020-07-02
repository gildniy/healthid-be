import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from itertools import compress

from graphql import GraphQLError

from healthid.apps.products.models import Product
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES


def validate_fields(promotion, **kwargs):
    for key, value in kwargs.items():
        if type(value) is str and value.strip() == "":
            raise GraphQLError('{} is required.'.format(key))
        if key == 'discount' and (value <= 0 or value > 100):
            raise GraphQLError(
                'discount must be greater than 0 but less than or equal to 100'
            )
        setattr(promotion, key, value)
    return promotion


def set_recommended_promotion(promotion_model, products):
    today_date = datetime.now()
    three_months = today_date + relativedelta(months=+3)
    one_month = today_date + relativedelta(months=+1)
    updated_items = 0
    for product in products:
        updated_items += 1
        expire_date = product.nearest_expiry_date
        if expire_date <= one_month.date():
            promotion_id = 3
        elif one_month.date() < expire_date <= three_months.date():
            promotion_id = 2
        else:
            promotion_id = 1
        promotion = get_model_object(promotion_model, 'id', promotion_id)
        promotion.products.add(product)
    return updated_items


def check_all_products_exist(product_ids):
    products = []
    for product_id in product_ids:
        product = get_model_object(Product, 'id', product_id)
        if not product.is_approved:
            raise GraphQLError(
                f'Product with id {product_id} hasn\'t been approved yet.'
            )
        products.append(product)
    return products


def add_products_to_promotion(promotion, product_ids):
    products = check_all_products_exist(product_ids)
    for product in products:
        promotion.products.add(product)
    return promotion


def remove_quotes(dictionary):
    """
    Remove quotes from dictionary
    """
    return json.dumps(dictionary).replace('"', "")


def check_approved_sales(returned_sales, sales_return_detail):
    is_valid = []
    approved_returns_ids = []
    for returned_sale in returned_sales:
        returned_sale_detail = get_model_object(
            sales_return_detail, 'id', returned_sale)
        if returned_sale_detail.is_approved:
            approved_returns_ids.append(returned_sale_detail.id)
            is_valid.append(False)
    if not all(is_valid):
        invalid_items = list(
            compress(approved_returns_ids,
                     [not item for item in is_valid]))
        message = SALES_ERROR_RESPONSES[
            "already_approved_sales_returns"].format(
            ",".join(map(str, invalid_items)))
        raise GraphQLError(message)
