import os
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from healthid.utils.despatch_util.despatch_email_util import (
    queue_emails_job)
from healthid.apps.stock.models import StockCountTemplate
from healthid.utils.sales_utils.sales_report import check_user_sales, send_sales_report
from healthid.utils.sales_utils.sale_performance import populate_sale_performace_table
from healthid.utils.stock_utils.daily_stock_report import generate_stock_reports
from healthid.utils.sales_utils.sale_velocity import calculate_sale_velocity
from healthid.utils.product_utils.batch_expiries import \
    notify_about_expired_products, notify_pusher_about_expired_products
from healthid.utils.stock_utils.stock_count_alert import \
    generate_stock_counts_notifications, schedule_templates
from healthid.utils.product_utils.product_expiry import \
    check_for_expiry_products
from healthid.utils.orders_utils.inventory_notification import \
    inventory_check
    

time_interval = os.environ.get('EXPIRY_NOTIFICATION_DURATION', '43200')
job_run_interval = int(settings.STOCK_JOB_TIME_INTERVAL)
generate_promotion_interval = os.environ.get('GENERATE_PROMOTION_INTERVAL',
                                             1440) 

scheduler = BackgroundScheduler()

scheduler.add_job(notify_about_expired_products,
                  'interval', minutes=int(time_interval))
scheduler.add_job(calculate_sale_velocity, 'cron',
                  hour=21, minute=00)
scheduler.add_job(generate_stock_reports, 'cron',
                  hour=22, minute=00)
scheduler.add_job(populate_sale_performace_table, 'cron',
                  hour=8, minute=00 )
scheduler.add_job(check_for_expiry_products, 'interval',
                  minutes=int(generate_promotion_interval))
scheduler.add_job(inventory_check, 'cron',
                  day_of_week='sun', hour=23, minute=50)
scheduler.add_job(notify_pusher_about_expired_products, 'cron',
                  day_of_week='mon', hour=9, minute=30)
scheduler.add_job(notify_pusher_about_expired_products, 'cron',
                  day_of_week='mon', hour=9, minute=30)

if not settings.TESTING:
    scheduler.add_job(queue_emails_job, 'interval', seconds=5)

scheduler.start()


def alert_counting():
    """
    Method starts a new job for stock counts notifications
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        generate_stock_counts_notifications, 'interval',
        minutes=job_run_interval)
    scheduler.start()


def start_schedule_templates():
    """
    Shedules a job for each of the template filtered
    """
    if not scheduler.state:
        scheduler.start()

    stock_templates = StockCountTemplate.objects.filter(
        scheduled=False, interval__gt=0)
    for template in stock_templates:
        scheduler.add_job(
            lambda: schedule_templates(template), 'interval',
            id='{}'.format(template.id),
            days=template.interval,
            start_date=template.created_at,
            end_date=template.end_on)
        template.scheduled = True
        template.save()


@receiver(post_delete, sender=StockCountTemplate)
def remove_scheduled_jobs(sender, instance, using, **kwargs):
    """
    Stops a schedule when a template is deleted if necessary
    """
    job_id = '{}'.format(instance.id)
    if scheduler.get_job(job_id) in scheduler.get_jobs():
        scheduler.remove_job(job_id)
