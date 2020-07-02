from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.orders import (order, approve_supplier_order,
                                                 edit_order, close_order,
                                                 send_supplier_order_emails,
                                                 mark_supplier_order_as_sent,
                                                 auto_order)

from healthid.apps.orders.models.orders import SupplierOrderDetails

from datetime import datetime


class TestOrders(BaseConfiguration):
    '''Class to test orders operations
    '''

    def test_initiate_order(self):
        '''Method to test that users can be able to initiate orders
        '''

        response = self.query_with_token(
            self.access_token, 
            order.format(
                outlet_id=self.outlet.id, 
                business_id=self.business.id
            )
        )

        self.assertEqual(
            "{0:%d} {0:%B} {0:%Y} {0:%I}:{0:%M}{0:%p}".format(datetime.now()),
            response['data']['initiateOrder']['order']['name']
        )
        
        self.assertNotIn('errors', response)

    def test_initiate_order_with_invalid_business_id(self):
        '''Method to test that users can be able to initiate orders
        '''
        response = self.query_with_token(
            self.access_token, order.format(outlet_id=self.outlet.id, business_id='12345678'))
        
        self.assertIn('errors', response)
        self.assertEquals(response['errors'][0]['message'], "The business ID you provided does not exists")

    def test_admin_approve_supplier_orders(self):
        """Test an admin can approve orders"""
        id1 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id

        id2 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id
        supplier_order_ids = """["{}", "{}"]""".format(id1, id2)
        response = self.query_with_token(
            self.access_token_master,
            approve_supplier_order.format(
                order_id=self.order.id,
                additional_notes=" ",
                supplier_order_ids=supplier_order_ids))
        self.assertNotIn('errors', response)

    def test_edit_initiated_order(self):
        '''Method to test that users can be edit to initiate orders
        '''
        response = self.query_with_token(
            self.access_token, edit_order.format(outlet_id=self.outlet.id,
                                                 order_id=self.order.id))
        self.assertNotIn('errors', response)

    def test_admin_approve_supplier_orders_with_invalid_ids(self):
        """Test an admin can approve orders"""
        supplier_order_ids = ["1233", "q3q4234"]
        response = self.query_with_token(
            self.access_token_master,
            approve_supplier_order.format(
                order_id=self.order.id,
                additional_notes=" ",
                supplier_order_ids=supplier_order_ids))
        self.assertIn('errors', response)

    def test_admin_supplier_orders_emails(self):
        """Test an admin can send supplier order emails"""
        id1 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id

        id2 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id

        supplier_order_ids = """["{}", "{}"]""".format(id1, id2)
        response = self.query_with_token(
            self.access_token_master,
            send_supplier_order_emails.format(
                order_id=self.order.id,
                supplier_order_ids=supplier_order_ids))
        self.assertNotIn('errors', response)

    def test_marking_supplier_orders_as_sent(self):
        """Test an admin can send supplier order emails"""
        id1 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id

        id2 = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id

        supplier_order_ids = """["{}", "{}"]""".format(id1, id2)
        response = self.query_with_token(
            self.access_token_master,
            mark_supplier_order_as_sent.format(
                order_id=self.order.id,
                supplier_order_ids=supplier_order_ids))
        self.assertNotIn('errors', response)

    def test_close_open_order(self):
        """ Test closing an open order """
        self.order = self.create_order(closed=False)
        product = self.product
        supplier = self.supplier
        supplier_order_form_id = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id
        response = self.query_with_token(
            self.access_token,
            close_order.format(
                supplier_order_form_id=supplier_order_form_id,
                supplier_id=supplier.id,
                product_id=product.id))
        self.assertNotIn('errors', response)
        self.assertEqual(
            response['data']['closeOrder']['message'],
            'Order has been closed successfully. 1 products received.')

    def test_close_closed_order(self):
        """ Test closing an already closed order """
        self.order = self.create_order(closed=False)
        product = self.product
        supplier = self.supplier
        supplier_order_form_id = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id
        response = self.query_with_token(
            self.access_token,
            close_order.format(
                supplier_order_form_id=supplier_order_form_id,
                supplier_id=supplier.id,
                product_id=product.id))
        self.assertNotIn('errors', response)
        self.assertEqual(
            response['data']['closeOrder']['message'],
            'Order has been closed successfully. 1 products received.')

    def test_auto_order(self):
        """Test that function works as expected
        """
        response = self.query_with_token(
            self.access_token,
            auto_order
        )
        self.assertNotIn('errors', response)
        self.assertIn('data', response)
        self.assertIn('autosuggestProductOrder', response['data'])
        self.assertTrue(isinstance(
            response['data']['autosuggestProductOrder'], list))
        self.assertListEqual([], response['data']['autosuggestProductOrder'])
