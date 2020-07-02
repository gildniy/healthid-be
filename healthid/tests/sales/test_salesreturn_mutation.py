from faker import Faker
from datetime import timedelta
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES
from healthid.tests.test_fixtures.sales_return import \
    initiate_sales_return_query, approve_sales_return
from healthid.tests.factories import (
    SaleFactory, OutletFactory, ProductFactory, ReceiptTemplateFactory,
    ReceiptFactory, SaleReturnFactory, SaleReturnDetailFactory,
    BatchInfoFactory)
from healthid.tests.base_config import BaseConfiguration

faker = Faker()


class TestCreateSaleReturn(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.sale = SaleFactory()
        self.outlet = OutletFactory()
        self.product = ProductFactory()
        self.batch = BatchInfoFactory()
        self.receipt_template = ReceiptTemplateFactory(outlet=self.outlet)
        self.receipt = ReceiptFactory(
            receipt_template=self.receipt_template, sale=self.sale)
        self.sales_return = SaleReturnFactory(
            outlet=self.outlet, sale=self.sale)
        self.sales_return_detail = SaleReturnDetailFactory(
            batch=self.batch, sales_return=self.sales_return)

        self.sales_return_data = {
            'outlet_id': self.outlet.id,
            'batch_id': self.batch.id,
            'sale_id': self.sale.id
        }
        self.approve_sales_return_data = {
            'sale_id': self.sale.id,
            'returned_sales_ids': []
        }

    def test_initiate_sales_return_success(self):
        """
        test sales return initiation success
        """
        resp = self.query_with_token(
            self.access_token, initiate_sales_return_query.format(
                **self.sales_return_data))
        self.assertIn('data', resp)
        self.assertEqual(
            resp['data']['initiateSalesReturn']['message'],
            "Return was initiated successfully"
        )

    def test_initiate_sales_return_wrong_sale(self):
        """
        test sales return initiation failure with wrong sale id
        """
        self.sales_return_data['outlet_id'] = 300
        resp = self.query_with_token(
            self.access_token, initiate_sales_return_query.format(
                **self.sales_return_data))
        self.assertIn('errors', resp)
        self.assertEqual(
            resp['errors'][0]['message'],
            OUTLET_ERROR_RESPONSES["inexistent_outlet"].format(
                "300"
            )
        )

    def test_initiate_sales_return_wrong_product(self):
        """
        test sales return initiation failure with non existing product
        """
        self.sales_return_data['batch_id'] = 0
        resp = self.query_with_token(
            self.access_token, initiate_sales_return_query.format(
                **self.sales_return_data))
        self.assertIn('errors', resp)
        self.assertEqual(
            resp['errors'][0]['message'],
            "There are no BatchInfo(s) matching IDs: 0."
        )

    def test_returnable_days(self):
        """
        tests sales return initiation failure due to
        return after 30 default preferred returnable days
        """
        sale = self.sale
        sale.created_at = sale.created_at - timedelta(days=40)
        sale.save()
        self.sales_return_data['sale_id'] = sale.id
        resp = self.query_with_token(
            self.access_token, initiate_sales_return_query.format(
                **self.sales_return_data))
        self.assertEqual(
            resp['errors'][0]['message'],
            'Product preferred returnable days are done')

    def test_approve_empty_sales_return(self):

        sales_return_id = self.sales_return.id

        self.approve_sales_return_data['sales_return_id'] = sales_return_id

        resp = self.query_with_token(self.access_token_master,
                                     approve_sales_return.format(
                                         **self.approve_sales_return_data))

        self.assertIn('errors', resp)
        self.assertEqual(
            resp['errors'][0]['message'],
            SALES_ERROR_RESPONSES["empty_sales_return"])

    def test_approve_sales_return_successfully(self):
        sales_return_id = self.sales_return.id

        sales_return_detail_id = self.sales_return_detail.id
        self.approve_sales_return_data['sales_return_id'] = sales_return_id
        self.approve_sales_return_data['returned_sales_ids'].\
            append(int(sales_return_detail_id))
        resp = self.query_with_token(self.access_token_master,
                                     approve_sales_return.format(
                                         **self.approve_sales_return_data))
        self.assertNotIn('errors', resp)
        self.assertEqual(
            resp['data']['approveSalesReturn']['message'],
            "Sales return approved successfully")

    def test_already_approved_sales_return(self):
        self.sales_return_detail = \
            SaleReturnDetailFactory(is_approved=True,
                                    batch=self.batch,
                                    sales_return=self.sales_return)

        self.approve_sales_return_data['sales_return_id'] = \
            self.sales_return.id

        self.approve_sales_return_data['returned_sales_ids'].append(
            int(self.sales_return_detail.id))

        resp = self.query_with_token(
            self.access_token_master, approve_sales_return.format(
                **self.approve_sales_return_data))
        self.assertIn('errors', resp)
        self.assertEqual(
            resp['errors'][0]['message'], "Sales returns with ids {} already approved".format(self.sales_return_detail.id))  # noqa
