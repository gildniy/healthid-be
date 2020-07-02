from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.orders import (
    order_details_status_change, approve_supplier_order)
from healthid.utils.messages.orders_responses import (
    ORDERS_SUCCESS_RESPONSES)
from healthid.apps.orders.models.orders import SupplierOrderDetails


class TestOrderStatus(BaseConfiguration):
    '''Class to test orders operations
    '''

    def test_admin_cannot_change_supplier_orders_status_with_invalid_ids(self):
        supplier_order_id = "q3q4234"
        response = self.query_with_token(
            self.access_token_master,
            order_details_status_change.format(
                supplier_order_id=supplier_order_id))
        self.assertIn('errors', response)

    def dont_approve_when_approved_field_false(self):
        id_ = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id
        response = self.query_with_token(
            self.access_token_master,
            order_details_status_change.format(
                supplier_order_id=id_))
        self.assertIn('errors', response)

    def test_marking_supplier_orders_status_to_approved(self):
        id__ = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id
        expected_success = ORDERS_SUCCESS_RESPONSES[
            'supplier_order_mark_status'].format("['"+id__+"']")
        supplier_order_ids = """["{}"]""".format(id__)
        self.query_with_token(
            self.access_token_master,
            approve_supplier_order.format(
                order_id=self.order.id,
                additional_notes=" ",
                supplier_order_ids=supplier_order_ids))
        response = self.query_with_token(
            self.access_token_master,
            order_details_status_change.format(
                supplier_order_id=id__))
        self.assertEqual(expected_success, response[
            'data']['markSupplierOrderStatusApproved']['message'])

    def only_admin_can_change_status(self):
        id_ = SupplierOrderDetails.objects.create(
            order=self.order,
            supplier=self.supplier,
        ).id
        response = self.query_with_token(
            self.access_token,
            order_details_status_change.format(
                supplier_order_id=id_))
        self.assertIn('errors', response)
