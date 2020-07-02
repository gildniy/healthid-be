from healthid.apps.profiles.models import Profile
from healthid.tests.receipts.base import ReceiptBaseCase
from healthid.tests.test_fixtures.receipts import mail_receipt
from healthid.tests.test_fixtures.sales import (create_sale,
                                                create_anonymous_sale)
from healthid.utils.messages.receipts_responses import (
    RECEIPT_SUCCESS_RESPONSES, RECEIPT_ERROR_RESPONSES)


class TestReceiptMailer(ReceiptBaseCase):
    def setUp(self):
        super().setUp()
        self.create_customer_data.pop('email')
        self.create_customer_data.pop('loyalty_member')
        self.customer = Profile.objects.create(
            **self.create_customer_data)
        self.sales_data = {
            "discount_total": 48.5,
            "amount_to_pay": 20,
            "change_due": 399,
            "paid_amount": 590,
            "payment_method": "cash",
            "outlet_id": self.outlet.id,
            "sub_total": 33,
            "batchId": self.batch_info.id,
            "quantity": 4,
            "discount": 0,
            "price": 21,
        }

    def test_mail_receipt_without_customer(self):
        self.create_receipt_template()
        sale_creation_mutation = self.query_with_token(
            self.access_token, create_anonymous_sale.format(
                **self.sales_data))
        receipt_id = sale_creation_mutation['data']['createSale']['receipt'][
            'id']
        response = self.query_with_token(
            self.access_token,
            mail_receipt.format(receipt_id=receipt_id)
        )
        self.assertEqual(
            RECEIPT_ERROR_RESPONSES['mailer_no_customer'],
            response['errors'][0]['message']
        )

    def test_mail_receipt_without_email(self):
        self.create_receipt_template()
        sale_creation_mutation = self.query_with_token(
            self.access_token, create_sale.format(
                **self.sales_data, customer_id=self.customer.id))
        receipt_id = sale_creation_mutation['data']['createSale']['receipt'][
            'id']
        response = self.query_with_token(
            self.access_token,
            mail_receipt.format(receipt_id=receipt_id)
        )
        self.assertEqual(
            RECEIPT_ERROR_RESPONSES['mailer_no_email'],
            response['errors'][0]['message']
        )

    def test_mail_receipt_to_customer(self):
        self.create_receipt_template()
        sale_creation_mutation = self.query_with_token(
            self.access_token, create_sale.format(
                **self.sales_data, customer_id=self.customer_1.id))
        receipt_id = sale_creation_mutation['data']['createSale']['receipt'][
            'id']
        response = self.query_with_token(
            self.access_token,
            mail_receipt.format(receipt_id=receipt_id)
        )
        self.assertEqual(
            RECEIPT_SUCCESS_RESPONSES["mailer_success"],
            response['data']['mailReceipt']['message']
        )
