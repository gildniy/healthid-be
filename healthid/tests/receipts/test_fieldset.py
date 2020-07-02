from healthid.tests.receipts.base import ReceiptBaseCase
from healthid.apps.receipts.models import Receipt
from healthid.tests.test_fixtures.fieldset import (
    create_fieldset, delete_fieldset)
from healthid.apps.sales.models import Sale


class ReceiptTestCase(ReceiptBaseCase):

    def test_create_fieldset(self):
        receipt_template = self.create_receipt_template()
        sale = Sale.objects.create(
            sales_person=self.user, outlet=self.outlet, amount_to_pay=10.00,
            sub_total=10.00, paid_amount=10.00, change_due=0.00,
            discount_total=10.00)
        response = self.query_with_token(
            self.access_token_master,
            create_fieldset(receipt_template.id, sale.id),
        )
        self.assertIsNotNone(response['data']['createFieldSet'])
        self.assertNotIn('errors', response)

    def test_receipt_model(self):
        field_set = self.create_fieldset()
        receipts = Receipt.objects.all()
        self.assertQuerysetEqual(
            receipts, [f'<Receipt: {field_set.id}>'])

    def test_delete_fieldset(self):
        fieldset = self.create_fieldset()
        response = self.query_with_token(
            self.access_token_master,
            delete_fieldset(fieldset.id))
        self.assertIn("success", response["data"]["deleteFieldSet"])
