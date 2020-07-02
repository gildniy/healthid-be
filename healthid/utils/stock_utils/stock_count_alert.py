import threading
from datetime import datetime, timedelta

from healthid.apps.stock.models import StockCountTemplate
from healthid.apps.events.models import Event, EventType
from healthid.utils.app_utils.database import (SaveContextManager)
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.notifications_utils.handle_notifications import notify


def generate_stock_counts_notifications():
    '''Method to generate notifications
    '''
    today = datetime.now()
    count_date = today+timedelta(days=1)
    stock_templates = StockCountTemplate.objects.filter(
        schedule_time__start_date__range=(today, count_date))
    if stock_templates:
        for template in stock_templates:
            assigned_users = template.assigned_users.all()
            to_email = assigned_users.values_list('email', flat=True)
            email_stock_template = 'email_alerts/stocks/stock_email.html'
            subject = 'Stock counts alert'
            date = datetime.strftime(
                template.schedule_time.start_date, "%d-%b-%Y")
            messg = f'Reminder for the scheduled stock count on {date}'
            context = {
                'schedule_time': date,
                'template_type': 'Stock counts notification',
                'small_text_detail': messg
            }
            send_mail = SendMail(email_stock_template,
                                 context, subject, to_email)
            thread = threading.Thread(target=notify_users(
                send_mail, assigned_users, messg),
                daemon=True)
            thread.start()


def notify_users(send_mail, assigned_users, message):
    '''
        Method to triger notifications
    '''
    notify(
        users=assigned_users,
        subject='Stock counts alert',
        body=message)

    send_mail.send()


def schedule_templates(template):
    """
    Creates a new record based on the template passed as an argument
    Arguments:
        template {instance} -- an instance of the stock template
    """
    new_start_date = template.schedule_time.start_date + \
        timedelta(days=template.interval)
    new_end_date = template.schedule_time.end_date + \
        timedelta(days=template.interval)
    template_instance = StockCountTemplate()

    event_type = EventType.objects.get(id=template.schedule_time.event_type.id)

    with SaveContextManager(template_instance) as stock_template:
        stock_template.outlet = template.outlet
        stock_template.end_on = template.end_on
        stock_template.interval = template.interval
        stock_template.created_by = template.created_by
        stock_template.scheduled = template.scheduled
        event = Event(
            start_date=new_start_date,
            end_date=new_end_date,
            event_title=f'Stock Count Reminder',
            description=f'Stock reminder count on auto scheduling',
            event_type=event_type
        )
        event.save()
        stock_template.schedule_time = event
        stock_template.save()
        stock_template.products.set(template.get_products())
        stock_template.assigned_users.set(template.get_assigned_users())
        stock_template.designated_users.set(template.get_designated_users())
    to_email = stock_template.assigned_users.values_list(
        'email', flat=True)
    email_stock_template = 'email_alerts/stocks/stock_email.html'
    subject = 'Stock counts alert'
    context = {
        'schedule_time': datetime.strftime(
            stock_template.schedule_time.start_date, "%d-%b-%Y"),
        'by': str(template.created_by.email),
        'template_type': 'Stock counts',
        'small_text_detail': 'Hello, you have been assigned to carry'
        ' out stock counts'
    }
    send_mail = SendMail(email_stock_template, context, subject, to_email)
    send_mail.send()
