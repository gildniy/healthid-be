from collections import namedtuple
from healthid.apps.outlets.models import Outlet
from healthid.apps.sales.sales_velocity import SalesVelocity
from healthid.apps.products.models import Product, ProductMeta
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.messages.sales_responses import \
    SALES_ERROR_RESPONSES


def send_manager_email(products, managers_email):
    """
    send manager an email copy

    Args:
        products (list): Outlet's product.
        managers_email (str): Email belonging to an outlet's manager

    Returns:
        None
    """
    mail_context = {
        'products': products,
    }
    mail = SendMail(
        to_email=[managers_email],
        subject='Inventory Notification',
        template='email_alerts/reorder_email.html',
        context=mail_context
    )
    mail.send()


def product_below_stock(outlet, business_products, is_cron_job=True):
    """
    Auto searches for products below specified reorder point/max

    Args:
        outlet (cls): Outlet instance.
        business_products (cls): Business's product instance.
        is_cron_job (bool): check to ensure function can be a cron

    Returns:
        list: tuple(product_name, quantity)
    """
    products_below_stock = []
    for product in business_products:
        reorder_point = product.reorder_point
        reorder_max = product.reorder_max

        if not reorder_point:
            reorder_point = outlet.outletpreference.reorder_point

        if not reorder_max:
            reorder_max = outlet.outletpreference.reorder_max

        remaining_stock = product.quantity_in_stock

        sales_velocity = ProductMeta.objects.filter(
            dataKey = 'Sale Velocity',
            product_id = product.id
        ).values_list('dataValue',flat=True).first() or 1

        sales_velocity = float(sales_velocity)

        minimum_product_unit = reorder_point * sales_velocity
        maximum_product_unit = reorder_max * sales_velocity

        if (is_cron_job and remaining_stock < maximum_product_unit) or \
           (remaining_stock <= minimum_product_unit):
            ProductValueObject = namedtuple('Product',
                                            'id product_name preferred_supplier backup_supplier suggested_quantity')
            product_name = product.product_name
            preferred_supplier = product.preferred_supplier
            backup_supplier = product.backup_supplier
            suggest_quantity_reorder = maximum_product_unit - remaining_stock
            products_to_reorder = \
                ProductValueObject(
                    id = product.id,
                    product_name=product_name,
                    preferred_supplier=preferred_supplier,
                    backup_supplier=backup_supplier,
                    suggested_quantity=suggest_quantity_reorder
                )
            products_below_stock.append(products_to_reorder)
    return products_below_stock


def inventory_check():
    """
    cron job alert if inventory goes below reorder point.

    Returns:
        None
    """
    outlets = Outlet.objects.all()
    for outlet in outlets:
        managers_email = outlet.get_manager.email
        outlet_products = Product.objects.filter(
            outlet=outlet.id,
            is_approved=True
        )
        products_to_reorder = product_below_stock(outlet, outlet_products)
        if products_to_reorder:
            send_manager_email(products_to_reorder, managers_email)


def autosuggest_product_order(outlet):
    """
    Alert if inventory goes below reorder max.

    Args:
        outlet (cls): Outlet instance.

    Returns:
        [], list of products and quantity to order for
    """
    business_products = Product.objects.filter(
        business=outlet.business.id,
        is_approved=True
    )
    products_to_reorder = product_below_stock(outlet,
                                              business_products,
                                              is_cron_job=False)
    if products_to_reorder:
        return products_to_reorder
    else:
        return []
