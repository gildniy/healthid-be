# 
# Write a script to set the outlet_id of all existing batches 
# to the assigned outlet of the user who created them.
# 
import csv
import datetime
import os

from django.utils import timezone
from django.conf import settings as djangoSettings

from healthid.apps.sales.models import Sale, Payments, SaleDetail
from healthid.utils.app_utils.send_mail import SendMail
from healthid.apps.outlets.models import OutletUser, Outlet
from healthid.apps.business.models import Business

EMAIL_LIST = [
    'shuaibualexander@gmail.com',
    'Bunmi.I.Adewunmi@gmail.com',
    's.banda911@googlemail.com'
]



def _send_mail(payments_filename, products_filename, to_email):
    """
        This function sends a mail to the specified mails
        Arguments:
            payments_filename : The filename of the payments csv
            products_filename : The filename of the products csv
            to_email : The email of recipients
    """
    email_verify_template = \
            'email_alerts/sales_report/stock_report.html'
    subject = 'Daily Sales Report'
    context = {
        'todays_date': f"{datetime.date.today()}",
        'payments_filename': payments_filename,
        'products_filename': products_filename
    }
    logger(f"products filename {products_filename}")
    logger(f"payments_filename {payments_filename}")
    send_mail = SendMail(
        email_verify_template, context, subject, to_email)
    send_mail.send()



def _write_csv(daily_sales, to_email, name_id):
    """
        This function writes a csv to the static directory
        to enable the file to be accesible outside via a link
        Arguments:
            daily_sales : A list containing the sales made for the day
            to_email : A list of emails who are reciepients addresses
            name_id : a number used to generate different filenames
    """
    todays_date = datetime.date.today()
    payments_filename = f"payments_report_{name_id}_{todays_date}.csv"
    products_filename = f"products_report_{name_id}_{todays_date}.csv"
    # store the file as a static file for easy serving
    path_to_payments_file = os.path.join(djangoSettings.BASE_DIR, 'static', payments_filename)
    path_to_products_file = os.path.join(djangoSettings.BASE_DIR, 'static', products_filename)
    
    # write csv for products break down
    with open(path_to_products_file, mode="w") as products_csv_file:
        product_fieldnames = [
            "Sale_Id",
            "Product_Id",
            "ProductName",
            "Quantity_Sold",
            "Cost_Per_item",
            "Total"
        ]
        writer = csv.DictWriter(products_csv_file, fieldnames=product_fieldnames)
        writer.writeheader()
        # for each product sold(sale detail), document it
        for daily_sale in daily_sales:
            sale_details = SaleDetail.objects.filter(
                sale_id = daily_sale.id
                )

            for sale_detail in sale_details:         
                writer.writerow(
                    {
                        "Sale_Id": daily_sale.id,
                        "Product_Id": sale_detail.product_id,
                        "ProductName": sale_detail.product.product_name,
                        "Quantity_Sold": sale_detail.quantity,
                        "Cost_Per_item": sale_detail.price,
                        "Total": sale_detail.price * sale_detail.quantity
                    }
                )

    # write csv for payments break down
    with open(path_to_payments_file, mode="w") as payments_csv_file:
        payments_fieldnames = [
            "Transaction_Date",
            "Transaction_Id",
            "Transaction_Type",
            "Cash",
            "Card",
            "Bank_Transfer",
            "Transaction_Total",
            "Cashier",
            "Customer",
            "Outlet"
        ]
        writer = csv.DictWriter(payments_csv_file, fieldnames=payments_fieldnames)
        writer.writeheader()

        for daily_sale in daily_sales:

            # Get payment details
            cash_payment = Payments.objects.filter(
                sale_id = daily_sale.id, 
                payment_method = "CASH"
                ).values_list('amount',flat=True).first() or 0
            card_payment = Payments.objects.filter(
                sale_id = daily_sale.id, 
                payment_method = "CARD"
                ).values_list('amount',flat=True).first() or 0
            transfer_payment = Payments.objects.filter(
                sale_id = daily_sale.id, 
                payment_method = "BANK_TRANSFER"
                ).values_list('amount',flat=True).first() or 0

            # write details to csv
            writer.writerow(
                {
                    "Transaction_Date": daily_sale.created_at,
                    "Transaction_Id": daily_sale.id,
                    "Transaction_Type": "Sale",
                    "Cash": cash_payment,
                    "Card": card_payment,
                    "Bank_Transfer": transfer_payment,
                    "Transaction_Total": daily_sale.amount_to_pay,
                    "Cashier": daily_sale.sales_person,
                    "Customer": daily_sale.customer,
                    "Outlet": daily_sale.outlet
                }
            )
    
    _send_mail(payments_filename, products_filename, to_email)

def logger(message):
    """
        create a basic logger
    """
    with open("debub.log", "a") as debug_file:
        debug_file.write(f"{message}\n")

def generate_stock_reports():
    """
        This function deletes old csv's present on the server
        and sends mails to the required people
    """
    logger(f"stock report program started at {datetime.datetime.now()}")
    static_directory = os.path.join(djangoSettings.BASE_DIR, 'static')
    # remove all previous csv's
    [
        os.remove(os.path.join(static_directory, file)) for file in os.listdir(static_directory) 
        if file.endswith(".csv")
    ]
    logger("deleted old files present on the server.")
    # get sales from today
    tolerance_date = timezone.now().replace(hour=0, minute=0, second=0)
    todays_total_sales = Sale.objects.filter(created_at__gt = tolerance_date)

    # send the full list to admins and developers
    _write_csv(todays_total_sales, EMAIL_LIST , "managers")
    logger("sent mail to managers")
    # for each outlet present, send the mail to the outlet manager
    outlets_present = set(todays_total_sales.values_list("outlet_id", flat=True))
    for outlet_present in list(outlets_present):
        # get the sales of the outlets
        outlets_sale_for_today = todays_total_sales.filter(outlet_id = outlet_present)
        # get the manager for the outlet
        outlet_manager = OutletUser.objects.filter(
            outlet_id = outlet_present,
            role_id = "mng000001"
        ).first()

        if outlet_manager:
            email_to = [outlet_manager.user.email]
        else:
            # get the admin of the business
            outlet_business = Outlet.objects.get(id = outlet_present).business
            email_to = [outlet_business.user.email]

        # send the csv to the outlet managers or business admins
        _write_csv(outlets_sale_for_today, email_to, outlet_present)
        logger(f"sent mail to outlet {outlet_present}")
    logger("")


