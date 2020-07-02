from django.db import models
from django.db.models.signals import pre_save

from healthid.models import BaseModel
from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.id_generator import ID_LENGTH, id_gen
from healthid.apps.products.models import Product
from healthid.apps.sales.models import Sale, SaleReturn
from healthid.apps.sales.models import SaleDetail
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.receipts.barcode import generate_barcode, generate_receipt_number
from healthid.utils.messages.receipts_responses import RECEIPT_ERROR_RESPONSES
from healthid.utils.app_utils.database import SaveContextManager, get_model_object
from healthid.utils.messages.receipts_responses import RECEIPT_SUCCESS_RESPONSES


class ReceiptTemplate(BaseModel):
    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    cashier = models.BooleanField(default=True)
    discount_total = models.BooleanField(default=True)
    receipt_no = models.BooleanField(default=True)
    receipt = models.BooleanField(default=True)
    subtotal = models.BooleanField(default=True)
    total_tax = models.BooleanField(default=True)
    amount_to_pay = models.BooleanField(default=True)
    purchase_total = models.BooleanField(default=True)
    change_due = models.BooleanField(default=True)
    loyalty = models.BooleanField(default=True)
    loyalty_earned = models.BooleanField(default=True)
    loyalty_balance = models.BooleanField(default=True)
    barcode = models.BooleanField(default=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    logo = models.URLField()
    footer_message = models.CharField(
        default=RECEIPT_SUCCESS_RESPONSES["footer_success"], max_length=255
    )

    def __str__(self):
        return self.id


class Receipt(BaseModel):
    """
    Receipt Model

    Attributes:
        scanned_number(int): Number embedded in the barcode
        footer(str): Footer of the receipt
        receipt_template(obj): Template that is used when generating the
                               fields of the receipt
        sale(obj): Sale to which the receipt belongs to
    """

    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    receipt_no = models.CharField(null=True, max_length=50)
    barcode_url = models.URLField(null=True)
    scanned_number = models.BigIntegerField(null=True)
    receipt_template = models.ForeignKey(
        ReceiptTemplate, on_delete=models.CASCADE, related_name="receipts"
    )
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, null=True)
    sales_return = models.ForeignKey(SaleReturn, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.id

    def create_receipt(self, sale, outlet_id):
        """
        generates a receipt for a sale

        Args:
            sale(obj): whose receipt is to be created
            outlet_id(int): id for the outlet the receipt belongs to

        Returns:
            receipt(obj): receipt for a sale
        """
        outlet = get_model_object(Outlet, "id", outlet_id)
        receipt_template = ReceiptTemplate.objects.filter(outlet=outlet).first()
        if not receipt_template:
            receipt_template = ReceiptTemplate.objects.create(outlet=outlet)
        receipt = Receipt(sale=sale, receipt_template=receipt_template)
        with SaveContextManager(receipt, model=Receipt) as receipt:
            return receipt

    @property
    def cashier(self):
        """
        Checks if cashier has been selected on the receipt template

        Returns:
            obj: user object if cashier is selected
            None: if cashier is not selected
        """
        if self.receipt_template.cashier:
            return self.sale.sales_person
        return None

    @property
    def change_due(self):
        """
        Checks if change_due has been selected on the receipt template

        Returns:
            decimal: change of the customer after the sale if change_due
                     has been selected
            None: if change_due is not selected
        """
        if self.receipt_template.change_due:
            return self.sale.change_due
        return None

    @property
    def discount_total(self):
        """
        Checks if discount_total has been selected on the receipt
        template

        Returns:
            decimal: total discount given out during the sale if
                     discount_total is selected
            None: if discount_total is not selected
        """
        if self.receipt_template.discount_total:
            return self.sale.discount_total
        return None

    @property
    def sub_total(self):
        """
        Checks if subtotal has been selected on the receipt template

        Returns:
            decimal: total discount given out during the sale if
                     discount_total is selected
            None: if sub_total is not selected
        """
        if self.receipt_template.subtotal:
            return self.sale.sub_total
        return None

    @property
    def total_tax(self):
        """
        Checks if tax has been selected on the receipt template

        Returns:
            decimal: total tax on the products being sold if total_tax
                     has been selected
            None: if total_tax is not selected
        """
        if self.receipt_template.total_tax:
            return 0.00
        return None

    @property
    def amount_to_pay(self):
        """
        Checks if amount_to_pay has been selected on the receipt
        template

        Returns:
            decimal: total amonunt the customer paid for the sale if
                     amount_to_pay has been selected
            None: if amount_to_pay is not selected
        """
        if self.receipt_template.amount_to_pay:
            return self.sale.amount_to_pay
        return None

    @property
    def purchase_total(self):
        """
        Checks if purchase_total has been selected on the receipt
        template

        Returns:
            decimal: discount added to sub total for the sale if
                     purchase_total has been selected
            None: if purchase_total is not selected
        """
        if self.receipt_template.purchase_total:
            sub_total = self.sale.sub_total
            return round(sub_total - (sub_total * self.sale.discount_total / 100), 2)
        return None

    @property
    def loyalty(self):
        """
        Checks if loyalty has been selected on the receipt template

        Returns:
            boolean: true if the customer is a loyalty member otherwise
                     false if loyalty has been selected
            None: if loyalty is not selected
        """
        if self.receipt_template.loyalty:
            return self.sale.customer.loyalty_member
        return None

    @property
    def loyalty_earned(self):
        """
        Checks if loyalty_earned has been selected on the receipt
        template

        Returns:
            integer: loyalty points the customer earned during the sale
                     if loyalty_earned has been selected
            None: if loyalty_earned is not selected
        """
        if self.receipt_template.loyalty_earned:
            return self.sale.loyalty_earned
        return None

    @property
    def loyalty_balance(self):
        """
        Checks if loyalty_balance has been selected on the receipt
        template

        Returns:
            integer: loyalty points of the customer who just made the
                     purchase if loyalty_balance has been selected
            None: if loyalty_balance is not selected
        """
        if self.receipt_template.loyalty_balance:
            customer = self.sale.customer
            if customer:
                return customer.loyalty_points
        return None

    @staticmethod
    def mail_receipt(receipt_id):
        """
        Sends a digital copy of a sales receipt to the customer

        Arguments:
            receipt_id: ID of receipt to send

        Returns:
            None
        """
        receipt = get_model_object(Receipt, "id", receipt_id)
        sale_details = SaleDetail.objects.filter(sale_id=receipt.sale.id)
        receipt_product_info = [
            {
                "product_name": get_model_object(
                    Product, "id", sold_item_detail.product_id
                ).product_name,
                "quantity_bought": sold_item_detail.quantity,
                "price": sold_item_detail.price,
                "discount": sold_item_detail.discount,
            }
            for sold_item_detail in sale_details
        ]
        if not receipt.sale.customer:
            raise AttributeError(RECEIPT_ERROR_RESPONSES["mailer_no_customer"])
        if not receipt.sale.customer.email:
            raise AttributeError(RECEIPT_ERROR_RESPONSES["mailer_no_email"])
        mail_context = {
            "receipt": receipt,
            "receipt_product_info": receipt_product_info,
            "sale": receipt.sale,
        }
        mail = SendMail(
            to_email=[receipt.sale.customer.email],
            subject=f"Purchase receipt from {receipt.sale.outlet.name}",
            template="email_alerts/receipts/sale_receipt.html",
            context=mail_context,
        )
        mail.send()


def generate_receipt_number_and_barcode(**kwargs):
    """
    Generates receipt barcode and receipt number
    """
    receipt = kwargs.get("instance")
    receipt.receipt_no = generate_receipt_number(receipt, Receipt)


pre_save.connect(generate_receipt_number_and_barcode, sender=Receipt)
