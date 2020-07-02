from healthid.tests.base_config import BaseConfiguration
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.tests.factories import (OrderFactory, SuppliersFactory, UserFactory)
from healthid.tests.test_fixtures.orders \
    import create_supplier_order, update_supplier_order, delete_supplier_order


class TestSupplierOrder(BaseConfiguration):
    """
    testing supplier order model
    """

    def setUp(self):
        super(TestSupplierOrder, self).setUp()
        self.user1 = UserFactory()
        self.order1 = OrderFactory()
        self.supplier1 = SuppliersFactory(user=self.user1)

        self.supplier_order_data = {
            'order_id' : self.order1.id,
            'supplier_id' : self.supplier1.id
        }

    def test_create_supplier_order(self):
        """
        tests the creation of supplier order
        """
        resp = self.query_with_token(
            self.access_token, create_supplier_order.format(**self.supplier_order_data)
        )
        self.assertEqual(
            resp['data']['createSupplierOrder']['message'],
            SUCCESS_RESPONSES["creation_success"].format("Suppiier Order")
        )

    def test_update_supplier_order(self):
        """
        tests the updating of supplier order
        """
        # create a new order
        self.query_with_token(
            self.access_token, create_supplier_order.format(**self.supplier_order_data)
        )
        # update it
        resp = self.query_with_token(
            self.access_token, update_supplier_order.format(**self.supplier_order_data)
        )
        self.assertEqual(
            resp['data']['updateSupplierOrder']['supplierOrder']['status'],
            'PENDING_APPROVAL'
        )

    def test_delete_supplier_order(self):
        """
        tests the deleting of a supplier order
        """
        # create a new order
        created = self.query_with_token(
            self.access_token, create_supplier_order.format(**self.supplier_order_data)
        )
        supplier_order_id = created['data']['createSupplierOrder']['supplierOrder']['id']
        # delete it
        resp = self.query_with_token(
            self.access_token, delete_supplier_order.format(supplier_order_id = supplier_order_id)
        )
        self.assertEqual(
            resp['data']['deleteSupplierOrder']['message'],
            SUCCESS_RESPONSES["deletion_success"].format("Supplier order")
        )
