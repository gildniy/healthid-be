from re import sub
import datetime
from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.products.models import (DispensingSize, Product,
                                           ProductCategory, BatchInfo, Quantity)
from healthid.apps.orders.models.orders import ProductBatch
from healthid.utils.product_utils.product import \
    generate_reorder_points_and_max
from healthid.utils.app_utils.get_user_business import get_user_business
from healthid.utils.app_utils.get_user_outlet import get_user_outlet


def map_quickbooks_data_helper(row, business, user, default_quickbox_supplier):
    product_name = row.get('Item Name')
    brief_description = row.get('Brief Description') or ''
    item_description = row.get('Item Description') or ''
    manufacturer = row.get('Manufacturer') or 'N/A'
    backup_supp = row.get('Vendor Name 2')
    price = row.get('Regular Price')
    base_unit_of_measure = row.get(
        'Base Unit of Measure')
    attributes = row.get('Attributes')
    preferred_supp = row.get('Vendor Name')
    department_name = row.get('Department Name')
    description = (brief_description+' '+item_description) if (
        brief_description+item_description) else 'N/A'
    qty_1 = row.get('Qty 1')
    qty_2 = row.get('Qty 2')
    global_upc = row.get('UPC')
    product_meta_args = {
        'Alternate Lookup': row.get('Alternate Lookup'),
        'Size': row.get('Size'),
        'Average Unit Cost': row.get('Average Unit Cost'),
        'MSRP': row.get('MSRP'),
        'Custom Price 1': row.get('Custom Price 1'),
        'Custom Price 2': row.get('Custom Price 2'),
        'Custom Price 3': row.get('Custom Price 3'),
        'Custom Price 4': row.get('Custom Price 4'),
        'global_upc': row.get('UPC'),
        'Order By Unit': row.get('Order By Unit'),
        'Sell By Unit': row.get('Sell By Unit'),
        'Item Type': row.get('Item Type'),
        'Income Account': row.get('Income Account'),
        'COGS Account': row.get('COGS Account'),
        'Asset Account': row.get('Asset Account'),
        'Print Tags': row.get('Print Tags'),
        'Unorderable': row.get('Unorderable'),
        'Serial Tracking': row.get('Serial Tracking'),
        'Department Code': row.get('Department Code'),
        'Vendor Code': row.get('Vendor Code'),
        'Qty 2': row.get('Qty 2'),
        'On Order Qty': row.get('On Order Qty'),
        'unit_cost': row.get('Order Cost')
    }
    preferred_supplier = Suppliers.objects.filter(
        supplier_id=preferred_supp).first()
    backup_supplier = Suppliers.objects.filter(
        supplier_id=backup_supp).first()
    existing_product = Product.objects.filter(
        global_upc=global_upc
    ).first()
    supplier_id = preferred_supplier.id if preferred_supplier else default_quickbox_supplier.id
    unit_cost = row.get('Order Cost') or 0
    qty = qty_1 or qty_2 or 0

    if int(qty) < 1:
        qty = 0
        
    if (not existing_product and product_name) or not global_upc :
        get_product_category, create_product_category =\
            ProductCategory.objects.get_or_create(
                name=department_name, business_id=business.id)
        product_category = get_product_category or create_product_category
        get_dispensing_size_id, create_dispensing_size_id =\
            DispensingSize.objects.get_or_create(
                name="NULL")
        dispensing_size = get_dispensing_size_id or create_dispensing_size_id
        product_instance = Product(
            product_name=product_name,
            description=description,
            brand='N/A',
            manufacturer=manufacturer,
            backup_supplier_id=backup_supplier.id if backup_supplier else None,
            dispensing_size_id=dispensing_size.id if dispensing_size else None,
            preferred_supplier_id=supplier_id,
            product_category_id=product_category.id if product_category else None,
            loyalty_weight=2,
            sales_price=price,
            vat_status=True,
            is_approved=True,
            business_id=business.id,
            is_active=True,
            user_id=user.id if user else None,
            global_upc=global_upc
        )

        return {
                'action':'create', 'product_instance': product_instance, 
                'product_meta_args': product_meta_args, 'supplier_id': supplier_id, 
                'unit_cost': unit_cost, 'qty': qty
                }

    else:
        get_product_category, create_product_category =\
            ProductCategory.objects.get_or_create(
                name=department_name, business_id=business.id)
        product_category = get_product_category or create_product_category

        # update the existing products whose fields are not constants with the new information
        existing_product.product_name=product_name
        existing_product.description=description
        existing_product.manufacturer=manufacturer
        existing_product.backup_supplier_id=backup_supplier.id if backup_supplier else None
        existing_product.preferred_supplier_id=supplier_id    
        existing_product.product_category_id=product_category.id if product_category else None
        existing_product.sales_price=price
        existing_product.business_id=business.id
        existing_product.user_id=user.id if user else None

        return {
                'action':'update', 'product_instance': existing_product, 
                'product_meta_args': product_meta_args,'supplier_id': supplier_id, 
                'unit_cost': unit_cost, 'qty': qty
                }


def map_retail_pro_data_helper(row, business, user, default_retail_pro_supplier):
    desc1 = row.get('Desc1').replace(
        '"', '').title() if row.get('Desc1') else ''
    desc2 = row.get('Desc2').replace(
        '"', '').title() if row.get('Desc2') else ''
    Attr = row.get('Attr') or ''
    size = row.get('Size') or ''
    str_oh_qty = row.get('Str OH Qty')
    cost = row.get('Cost')
    price = row.get('Price')
    global_upc = row.get('Global UPC')
    vend_code = row.get('Vend Code')
    dcs = row.get('DCS')
    name = desc1+Attr+size
    product_name = desc1 + ' '+Attr + ' ' + size
    if not desc2:
        desc2 = 'N/A'

    product_meta_args = {
        'global_upc': global_upc,
        'str_oh_qty': str_oh_qty,
        'cost': cost,
        'price': price
    }

    supplier = Suppliers.objects.filter(supplier_id=vend_code).first()
    existing_product = Product.objects.filter(
        global_upc=global_upc
    ).first()
    get_dispensing_size_id, create_dispensing_size_id =\
        DispensingSize.objects.get_or_create(
            name="NULL")
    get_product_category, create_product_category =\
        ProductCategory.objects.get_or_create(
            name=dcs, business_id=business.id
        )

    supplier_id = supplier.id if supplier else default_retail_pro_supplier.id
    unit_cost = cost or 0
    qty = str_oh_qty or 0
    if int(qty) < 1:
        qty = 0
    
    if (not existing_product and name) or not global_upc:
        get_product_category, create_product_category =\
        ProductCategory.objects.get_or_create(
            name=dcs, business_id=business.id
        )

        product_instance = Product(
            product_name=desc1 + ' '+Attr + ' ' + size,
            description=desc2,
            brand='N/A',
            manufacturer='N/A',
            backup_supplier_id=None,
            dispensing_size_id=get_dispensing_size_id.id or
            create_dispensing_size_id.id,
            preferred_supplier_id=supplier_id,
            product_category_id=get_product_category.id or
            create_product_category.id,
            loyalty_weight=2,
            sales_price=price,
            vat_status=True,
            is_approved=True,
            business_id=business.id,
            auto_price=auto_calculate_price(price),
            global_upc = global_upc

        )
        supplier_id = supplier.id if supplier else default_retail_pro_supplier.id

        return {
            'action':'create',
            'product_instance': product_instance, 'product_meta_args': product_meta_args,
            'supplier_id': supplier_id, 'unit_cost': unit_cost, 'qty': qty
            }
    else:
        existing_product.product_name=desc1 + ' '+Attr + ' ' + size
        existing_product.dispensing_size_id=get_dispensing_size_id.id or create_dispensing_size_id.id
        existing_product.preferred_supplier_id=supplier_id
        existing_product.product_category_id=get_product_category.id or create_product_category.id
        existing_product.sales_price=price
        existing_product.business_id=business.id
        existing_product.auto_price=auto_calculate_price(price)
        existing_product.description = desc2

        return {
            'action':'update',
            'product_instance': existing_product, 'product_meta_args': product_meta_args,
            'supplier_id': supplier_id, 'unit_cost': unit_cost, 'qty': qty
        }


def auto_calculate_price(price):
    x = False if price else True
    return x


def create_batch_helper(product, user, supplier_id, unit_cost, qty, tag="BN"):
    date_received = datetime.date.today().strftime('%Y-%m-%d')
    datetime_str = sub(
        '[.]', '', str(datetime.datetime.timestamp(datetime.datetime.now())))
    batch_no_auto = f'{tag}{datetime_str}'
    user_outlet = get_user_outlet(user)
    user_business = get_user_business(user)

    product_batch = ProductBatch(
        unit_cost = unit_cost,
        status = "IN_STOCK",
        quantity = int(qty),
        expiry_date = datetime.date.today() + datetime.timedelta(days=365),
        date_received = date_received,
        batch_ref = batch_no_auto, 
        product_id = product.id,
        supplier_id = supplier_id,
        business = user_business,
        outlet_id = user_outlet.id
    )
    product_batch.save()
    # update the properties of the product, now that a new product batch has been added
    product.update_inventory()


def create_out_of_stock_batch(product, user, supplier_id, unit_cost):
    date_received = datetime.date.today().strftime('%Y-%m-%d')
    user_outlet = get_user_outlet(user)
    user_business = get_user_business(user)

    product_batch = ProductBatch(
        unit_cost = unit_cost,
        status = "IN_STOCK",
        quantity = 99,
        expiry_date = '2099-01-01',
        date_received = date_received,
        batch_ref = 'OUT OF STOCK', 
        product_id = product.id,
        supplier_id = supplier_id,
        business = user_business,
        outlet_id = user_outlet.id
    )
    product_batch.save()