from healthid.tests.base_config import BaseConfiguration
from healthid.apps.receipts.models import ReceiptTemplate, Receipt
from healthid.apps.sales.models import Sale


class ReceiptBaseCase(BaseConfiguration):
    def create_receipt_template(self):
        outlet = self.outlet
        return ReceiptTemplate.objects.create(
            cashier=False, discount_total=False, outlet_id=outlet.id,
            total_tax=True, subtotal=True, purchase_total=True,
            change_due=False, loyalty=True, amount_to_pay=False, receipt=False,
            receipt_no=True)

    def create_fieldset(self):
        sale = Sale.objects.create(
            sales_person=self.user, outlet=self.outlet, amount_to_pay=10.00,
            sub_total=10.00, paid_amount=10.00, change_due=0.00,
            discount_total=10.00)
        receipt_template = self.create_receipt_template()
        return Receipt.objects.create(
            receipt_template_id=receipt_template.id, sale=sale)
