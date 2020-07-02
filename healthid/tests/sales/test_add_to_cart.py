from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.sales import add_to_cart
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES


class TestCreateCart(BaseConfiguration):
    def test_user_can_add_product_to_cart(self):
        response = self.query_with_token(self.access_token_master,
                                         add_to_cart(self.product.id, 1))
        self.assertIn('success', response['data']['addToCart'])
        self.assertNotIn('errors', response)

    def test_user_cannot_add_unapproved_product_to_cart(self):
        self.product.is_approved = False
        self.product.save()
        response = self.query_with_token(self.access_token_master,
                                         add_to_cart(self.product.id, 1))
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES[
                         "unapproved_product_error"].format(
            self.product.product_name))

    def test_user_cant_add_product_to_cart_with_quantity_than_available(self):
        product = self.product
        response = self.query_with_token(self.access_token_master,
                                         add_to_cart(
                                             product.id,
                                             product.quantity_in_stock + 10))
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES[
                         "in_stock_product_error"].format(
            product.quantity_in_stock, product.product_name))

    def test_user_cant_add_product_to_cart_when_unathenticated(self):
        response = self.query_with_token('', add_to_cart(self.product.id, 1))
        self.assertIsNotNone(response['errors'])
