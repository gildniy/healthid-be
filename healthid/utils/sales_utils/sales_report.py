from healthid.apps.sales.models import BatchHistory
from healthid.apps.outlets.models import Outlet
from healthid.apps.business.models import Business
from healthid.utils.app_utils.send_mail import SendMail
from healthid.apps.sales.models import Sale
from django.contrib.auth import get_user_model
import pytz
import datetime
from django.db.models import Sum, Count



date_today_before = datetime.datetime.now().replace(
    hour=0, minute=0, second=0, microsecond=000000)
date_today_after = datetime.datetime.now().replace(
    hour=23, minute=59, second=59, microsecond=999999)


def send_sales_report():

    businesses = Business.objects.all()
    for business in businesses:
        generate_report(business.id, str(business.user))


def generate_report(business_id, user_email):
    sales_data = check_user_sales()
    for index in range(len(sales_data)):
        for key in sales_data[index].keys():
            if key == business_id:
                sale_performance = sales_data[index][''+key+'']

    to_email = [
        user_email
        ]
    sales_report_template = \
        'email_alerts/sales_report/sales_report_email.html'
    subject = 'Sales Report'
    context = {
        'date': datetime.datetime.now(),
        'template_type': 'Sales Report Summary',
        'data': sale_performance
    }
    send_mail = SendMail(
        sales_report_template, context, subject, to_email)
    send_mail.send()

def check_user_sales():
    businesses = business_list()
    outlets_businesses = outlets_business(businesses)
    return outlets_businesses


def calculate_sales(outlet_id):

    info = []
    users = BatchHistory.objects.filter(created_at__gte=date_today_before).filter(
        created_at__lte=date_today_after).filter(sale__outlet_id=outlet_id).distinct('sale__sales_person_id')


    for user in users:
        user_info = {}
        user_info['user_id'] = user.sale.sales_person_id
        user_info['user_name'] = f'{user.sale.sales_person.first_name}, {user.sale.sales_person.email}, {user.sale.sales_person.role.name}'
        user_info['Total_number_of_Products_sold'] = person_sales_total(user.sale.sales_person_id, outlet_id, 'total_number_per_day')
        user_info['Total_qty_of_Products_sold'] = person_sales_total(user.sale.sales_person_id, outlet_id, 'total_qty_per_day')
        user_info['total_cash_per_day'] = person_sales_total(user.sale.sales_person_id, outlet_id, 'person_cash_per_day')
        user_info['total_card_per_day'] = person_sales_total(user.sale.sales_person_id, outlet_id, 'person_card_per_day')
        user_info['total_amount_day'] = person_sales_total(user.sale.sales_person_id, outlet_id, 'total_amount_day')
        user_info['product_list'] = person_sales_total(user.sale.sales_person_id, outlet_id, 'product_list')
        info.append(user_info)
    return info


def person_sales_total( id, outlet_id ,types):
    if types == 'total_number_per_day':
        total_number_per_day = BatchHistory.objects.filter(created_at__gte=date_today_before).filter(
            created_at__lte=date_today_after).filter(sale__sales_person_id=id).filter(sale__outlet_id=outlet_id).aggregate(number=Count('product__product_name'))
        return total_number_per_day['number']
    elif types == 'person_cash_per_day':
        amount_in_cash = BatchHistory.objects.filter(created_at__gte=date_today_before).filter(
            created_at__lte=date_today_after).filter(sale__sales_person_id=id).filter(sale__outlet_id=outlet_id).filter(sale__payment_method='cash').aggregate(Sum_cash=Sum('sale__paid_amount'))
        return amount_in_cash['Sum_cash']
    elif types == 'person_card_per_day':
        amount_in_card = BatchHistory.objects.filter(created_at__gte=date_today_before).filter(
            created_at__lte=date_today_after).filter(sale__sales_person_id=id).filter(sale__outlet_id=outlet_id).filter(sale__payment_method='card').aggregate(Sum_card=Sum('sale__paid_amount'))
        return amount_in_card['Sum_card']
    elif types == 'total_qty_per_day':
        total_qty_per_day = BatchHistory.objects.filter(created_at__gte=date_today_before).filter(
            created_at__lte=date_today_after).filter(sale__sales_person_id=id).filter(sale__outlet_id=outlet_id).aggregate(qty=Sum('quantity_taken'))
        return total_qty_per_day['qty']
    elif types == 'total_amount_day':
        total_amount_day = BatchHistory.objects.filter(sale__sales_person_id=id).filter(sale__outlet_id=outlet_id).filter(created_at__gte=date_today_before).filter(
            created_at__lte=date_today_after).aggregate(total_amount_day=Sum('sale__paid_amount'))
        return total_amount_day['total_amount_day']
    elif types == 'product_list':
        list_item = []
        product_list = BatchHistory.objects.filter(created_at__gte=date_today_before).filter(sale__outlet_id=outlet_id).filter(created_at__lte=date_today_after).filter(sale__sales_person_id=id)
        for i in product_list:
            item = {}
            item['product_name'] = i.product.product_name
            item['qty_sold'] = i.quantity_taken
            item['batch_nbr'] = i.batch_info.id
            item['expire_date'] = i.batch_info.expiry_date
            list_item.append(item)
        return list_item


def business_list():
    business_ids = Business.objects.all()
    ids = [{f'{business.id}':None} for business in business_ids]
    return ids


def outlets_business(business_list):
    business = business_list
    for index in range(len(business)):
        for key in business[index].keys():
            business[index][''+key+''] = []
            outlet_one = Outlet.objects.filter(business_id = f'{key}')
            for i in outlet_one:
                obj = {}
                obj['id'] = i.id
                obj['name'] = i.name
                obj['total_number_sold'] = outlet_sales_total(i.id, 'number_sold')
                obj['total_qty_sold'] = outlet_sales_total(i.id,'qty_sold')
                obj['total_amount_cash'] = outlet_sales_total(i.id, 'cash')
                obj['total_amount_card'] = outlet_sales_total(i.id, 'card')
                obj['sold_amount'] = outlet_sales_total(i.id, 'sold_amount')
                obj['salers'] = calculate_sales(i.id)
                business[index][''+key+''].append(obj)
    return business

def outlet_sales_total(key, types):
    if types == 'number_sold':
        total_number_product = BatchHistory.objects.filter(sale__outlet_id=key).filter(
            created_at__gte=date_today_before).filter(created_at__lte=date_today_after).aggregate(total_pro=Count('product__product_name'))
        return total_number_product['total_pro']
    elif types == 'qty_sold':
        total_sold_product = BatchHistory.objects.filter(sale__outlet_id=key).filter(
        created_at__gte=date_today_before).filter(created_at__lte=date_today_after).aggregate(total_pro=Sum('quantity_taken'))
        return total_sold_product['total_pro']
    elif types == 'cash':
        total_cash = BatchHistory.objects.filter(sale__outlet_id=key).filter(created_at__gte=date_today_before).filter(created_at__lte=date_today_after).filter(sale__payment_method='cash').aggregate(total_cash=Sum('sale__paid_amount'))
        return total_cash['total_cash']
    elif types == 'card':
        total_card = BatchHistory.objects.filter(sale__outlet_id=key).filter(
            created_at__gte=date_today_before).filter(created_at__lte=date_today_after).filter(sale__payment_method='card').aggregate(total_card=Sum('sale__paid_amount'))
        return total_card['total_card']
    elif types == 'sold_amount':
        sold_amount = BatchHistory.objects.filter(sale__outlet_id=key).filter(created_at__gte=date_today_before).filter(created_at__lte=date_today_after).aggregate(total_day=Sum('sale__paid_amount'))
        return sold_amount['total_day']

