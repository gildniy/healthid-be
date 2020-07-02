from django.utils import timezone
from graphql import GraphQLError
from healthid.utils.app_utils.database import SaveContextManager
from django.conf import settings
from healthid.apps.products.models import Product, ProductMeta, BatchInfo, Quantity
from healthid.apps.orders.models.orders import ProductBatch
from healthid.utils.app_utils.get_user_business import get_user_business
from healthid.utils.app_utils.get_user_outlet import get_user_outlet
from healthid.utils.product_utils.metadata_handler import add_product_metadata, product_meta_object, update_product_metadata
from datetime import date


def set_product_attributes(product, **kwargs):
    tags = kwargs.pop("tags", None)
    for (key, value) in kwargs.items():
        if isinstance(value, str) and value.strip() == "":
            raise GraphQLError("The {} field can't be empty".format(key))
        if key == 'id':
            continue
        setattr(product, key, value)
    with SaveContextManager(product, model=Product):
        if tags is not None:
            product.tags.set(*tags)

        add_product_meta(product)

        return product


def add_product_meta(product):
    product_meta_already_exits = ProductMeta.objects.filter(
        product_id=product.id)

    product_meta_data = extract_product_meta_data(product)

    # if the product has metadata and the incoming product contains metadata then update it's metadata
    if(product_meta_already_exits and product_meta_data):
        update_product_metadata(product, product_meta_data)

    # if it reaches here, then it's a new product, so save the metadata of the new product as well
    elif(product_meta_data):
        add_product_metadata(product, product_meta_data)

def extract_product_meta_data(product):
    product_meta_data = {}
    for (key, value) in product.__dict__.items():
        if key in product_meta_object and value:
            product_meta_data[key] = value
    return product_meta_data

def generate_reorder_points_and_max(user_id, product_instance):
    """
        this function generates reorder points and reorder
        max basing on the weekly average unit sales of a product

    """
    average_weekly_sales = settings.MOCK_AVERAGE_WEEKLY_SALES
    reorder_point = average_weekly_sales * 3
    reorder_max = average_weekly_sales * 6
    product_instance.reorder_point = reorder_point
    product_instance.reorder_max = reorder_max
    product_instance.save()
    add_product_meta(product_instance)


def update_new_batch_number_to_out_of_stock(batch):
    BatchInfo.objects.filter(id=batch.id).update(batch_no='OUT OF STOCK')

def addOutOfStockBatch(user, product):
    batch_already_exists = ProductBatch.objects.filter(batch_ref='OUT OF STOCK', product_id=product.id)
    if product.is_approved and not batch_already_exists:

        product_batch = ProductBatch()
        
        product_batch.unit_cost = product.sales_price or 0
        product_batch.quantity = 99
        product_batch.status = 'IN_STOCK'
        product_batch.expiry_date = '2099-01-01'
        product_batch.date_received = timezone.now()
        product_batch.batch_ref = 'OUT OF STOCK'
        product_batch.product = product
        product_batch.supplier = product.preferred_supplier
        product_batch.business = get_user_business(user)
        product_batch.outlet = get_user_outlet(user)

        product_batch.save()
        


def addOutOfStockQuantity(batch_info, quantity=99):
    quantity = Quantity(
        batch=batch_info, quantity_received=quantity,
        quantity_remaining=quantity, is_approved=True)
    quantity.save()
