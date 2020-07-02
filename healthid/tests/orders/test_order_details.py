from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import supplier_mutation
from healthid.tests.test_fixtures.orders import (
    add_quantities, add_suppliers, add_product_manually,
    assign_suppliers_to_different_products)
from healthid.tests.test_fixtures.orders import order as initiate_order
from healthid.tests.test_fixtures.orders import (products_query,
                                                 suppliers_autofill)
from healthid.tests.test_fixtures.business import create_orders_products


class OrderDetailsTestCase(BaseConfiguration):
    def setUp(self):
        super().setUp()
        # self.supplier = self.query_with_token(self.access_token_master,
        #                                       supplier_mutation)
        # self.supplier_id = self.supplier['data']['addSupplier']['supplier'][
        #     'id']
        order = self.query_with_token(
            self.access_token, initiate_order.format(outlet_id=self.outlet.id, business_id=self.business.id))
        self.details_dict = {
            'order_id': order['data']['initiateOrder']['order']['id'],
            'product': self.product.id
        }
        self.product.reorder_max = 50
        self.product.reorder_point = 30
        self.product.save()

        self.orders_products = create_orders_products(
            self.order.id,
            self.product
        )

    def test_suppliers_autofill(self):
        response = self.query_with_token(
            self.access_token, suppliers_autofill.format(**self.details_dict))

        self.assertIn('Successfully',
                      response['data']['addOrderDetails']['message'])

    def test_add_suppliers(self):
        self.details_dict['supplier'] = self.supplier.id
        response = self.query_with_token(
            self.access_token, add_suppliers.format(**self.details_dict))
        self.assertIn('Successfully',
                      response['data']['addOrderDetails']['message'])

    def test_add_quantities(self):
        response = self.query_with_token(
            self.access_token, add_quantities.format(**self.details_dict))
        self.assertIn('Successfully',
                      response['data']['addOrderDetails']['message'])

    def test_query_products_with_low_quantity(self):
        response = self.query_with_token(
            self.access_token, products_query)
        self.assertIsNotNone(response['data']['productAutofill'])

    def test_add_product_manually(self):
        response = self.query_with_token(
            self.access_token,
            add_product_manually.format(
                order_id=self.order.id, product_id=self.product.id)
        )
        self.assertEqual(f"Successfully added 1 product(s)",
                         response["data"]["manual_add_product"]["message"])

    def test_add_supplier_manually(self):
        product_ids = [self.product.id]
        self.supplier = self.query_with_token(self.access_token_master, supplier_mutation)
        self.supplier_id = self.supplier['data']['addSupplier']['supplier'][
            'id']
        response = self.query_with_token(
            self.access_token,
            assign_suppliers_to_different_products.format(
                order_id=self.order.id, row_ids=product_ids, supplier_id=self.supplier_id)
        )
        self.assertEquals(len(response["data"]["assignSuppliersToProducts"]["addedProductDetails"]), len(product_ids))
