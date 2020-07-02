from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.invoices import upload_invoice
from healthid.tests.test_fixtures.orders import order as initiate_order
from mock import patch
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class InvoiceTestCase(BaseConfiguration):
    def setUp(self):
        super().setUp()
        order = self.query_with_token(
            self.access_token,
            initiate_order.format(outlet_id=self.outlet.id)
        )
        self.details_dict = {
            'order_id': order['data']['initiateOrder']['order']['id'],
        }

    def test_empty_image_url(self):
        """Test that url supplied is a valid one
        """
        self.invoice_data["image_url"] = ""
        self.invoice_data["order_id"] = self.details_dict['order_id']
        response = self.query_with_token(
            self.access_token,
            upload_invoice.format(**self.invoice_data))
        expected_message = "Invoice file field cannot be blank!"
        self.assertEqual(
            expected_message,
            response["errors"][0]["message"])

    @patch('cloudinary.uploader.upload')
    def test_upload_invoice(self, mock):
        """Test that an invoice can be uploaded
        """
        mock.return_value = {'url': 'sgs'}
        self.invoice_data["order_id"] = self.details_dict['order_id']
        response = self.query_with_token(
            self.access_token,
            upload_invoice.format(**self.invoice_data))
        expected_message = SUCCESS_RESPONSES[
                           "upload_success"].format("Invoice")
        self.assertEqual(
            expected_message,
            response["data"]["uploadInvoice"]["message"])
        self.assertNotIn("errors", response)

    def test_invalid_image_url(self):
        """Test that url supplied is a valid one
        """
        self.invoice_data["image_url"] = "jgjgjgj"
        self.invoice_data["order_id"] = self.details_dict['order_id']
        response = self.query_with_token(
            self.access_token,
            upload_invoice.format(**self.invoice_data))
        expected_message = "[Errno 2] No such file or directory: 'jgjgjgj'"
        self.assertEqual(
            expected_message,
            response["errors"][0]["message"])
