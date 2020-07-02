from itertools import groupby
from datetime import datetime
from healthid.apps.products.models import BatchInfo
from healthid.apps.sales.models import Promotion, PromotionType
from healthid.utils.app_utils.database import SaveContextManager
from healthid.utils.notifications_utils.handle_notifications import notify


def check_for_expiry_products():
    """
    Check for products about to expire
    """

    batches = BatchInfo.objects.filter(sold_out=False)
    batches_by_outlets = [list(result) for key, result in groupby(
        batches, key=lambda batch: batch.product.business.outlet_set.first())]
    today = datetime.today().date()
    for batches_per_outlet in batches_by_outlets:
        expire_in_six_months = []
        expire_in_three_months = []
        expire_in_one_month = []
        for batch in batches_per_outlet:
            expiry_date = batch.expiry_date
            days_to_expiry = (expiry_date - today).days
            outlet = batch.product.business.outlet_set.first()
            if 182 >= days_to_expiry > 91:
                expire_in_six_months.append(batch.product)
            elif 91 >= days_to_expiry > 30:
                expire_in_three_months.append(batch.product)
            elif 30 >= days_to_expiry > 0:
                expire_in_one_month.append(batch.product)
        if expire_in_six_months:
            title = f'Expire in 6 months {outlet.id}'
            create_promotion(expire_in_six_months, title, 20, outlet)
        if expire_in_three_months:
            title = f'Expire in 3 months {outlet.id}'
            create_promotion(expire_in_three_months, title, 40, outlet)
        if expire_in_one_month:
            title = f'Expire in 1 month {outlet.id}'
            create_promotion(expire_in_one_month, title, 60, outlet)


def create_promotion(products, title, discount, outlet):
    '''
    Create promotion for products about to expiry
    '''
    promotion = Promotion.objects.filter(title=title).first()
    products_added = True
    if promotion:
        products_added = not all(
            product in products for product in promotion.products.all())
        promotion.products.add(*products)
    else:
        promotion_type, _ = PromotionType.objects.get_or_create(name='expiry')
        description = 'Products about to expire.'
        promotion = Promotion(title=title, promotion_type=promotion_type,
                              description=description, discount=discount,
                              is_approved=False, outlet=outlet)
        with SaveContextManager(promotion, model=Promotion) as promotion:
            promotion.products.add(*products)
    if products_added:
        users = outlet.active_outlet_users
        roles = ('Master Admin', 'Manager')
        users = [user for user in users if str(user.role) in roles]
        message = f'Products have been added to promotion {title}.'
        notify(users=users, subject='Products about to expire.', body=message)
