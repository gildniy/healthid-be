import threading
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.template.loader import render_to_string
from healthid.apps.products.models import BatchInfo
from healthid.utils.notifications_utils.handle_notifications import notify


def notify_about_expired_products():
    '''Method to extract expired batches from the database
    '''
    expired_batches = []
    today = datetime.today().date()
    batches = BatchInfo.objects.all()
    if batches:
        for batch in batches:
            expiry_date = batch.expiry_date
            days_to_expiry = (expiry_date - today).days
            if days_to_expiry <= 365:
                batch = {
                    'batch': batch,
                    'days_to_expiry': days_to_expiry
                }
                expired_batches.append(batch)
        thread = threading.Thread(
            target=trigger_notification(expired_batches),
            daemon=True)
        thread.start()


def trigger_notification(expired_batches):
    '''Method to trigger a notification to Master Admin users
    '''

    for batch in expired_batches:
        outlet = batch['batch'].outlet

        users = outlet.active_outlet_users
        outlet_master_admins = [
            user for user in users if str(user.role) == 'Master Admin']
        batch_number = batch["batch"].batch_no
        message = f'Products with batch no. { batch_number } are within \
12 months to expiry!'

        products = batch['batch'].product.all()
        product_names = [product.product_name for product in products]
        html_body = render_to_string(
            'batch_expiries/expiry_notification.html',
            {
                'batch': batch['batch'],
                'product': product_names,
                'outlet': batch['batch'].outlet.name,
                'days_to_expiry': batch["days_to_expiry"]
            })
        subject = 'Expired Products!'
        event_name = 'batch-expiry-notification-event'
        thread = threading.Thread(target=notify(users=outlet_master_admins,
                                                subject=subject,
                                                body=message,
                                                event_name=event_name,
                                                html_body=html_body))
        thread.start()


def generate_expiry_notification(expired_batches):
    '''Method to trigger a notification to users
    '''
    expired_products = []
    outlet_user = []
    for batch in expired_batches:
        outlet = batch['batch'].product.business.outlet_set.first()
        for user in outlet.active_outlet_users:
            outlet_user.append(user)
        message = {
            'id': batch['batch'].id,
            'batch': batch['batch'].batch_no,
            'product': batch['batch'].product.product_name,
            'outlet': batch['batch'].product.business.outlet_set.first().name,
            'days_to_expiry': batch["days_to_expiry"]
        }
        expired_products.append(message)
    event_name = 'expiry-notification-event'
    thread = threading.Thread(target=notify(users=outlet_user,
                                            subject='Expired Products!',
                                            body=message,
                                            event_name=event_name, ))
    thread.start()


def notify_pusher_about_expired_products():
    '''Method to extract expired batches from the database
    '''
    expired_batches = []
    today = datetime.today().date()
    twelve_months = today + relativedelta(months=+12)
    batches = BatchInfo.objects.all()
    if batches:
        for batch in batches:
            expiry_date = batch.expiry_date
            days_to_expiry = (today - expiry_date).days
            if expiry_date <= twelve_months:
                batch = {
                    'batch': batch,
                    'days_to_expiry': days_to_expiry
                }
                expired_batches.append(batch)
    thread = threading.Thread(
        target=generate_expiry_notification(expired_batches),
        daemon=True)
    thread.start()
