from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.sales import retrieve_cart


class TestRetrieveCart(BaseConfiguration):
    def test_user_can_retrieve_a_cart(self):
        response = self.query_with_token(self.access_token_master,
                                         retrieve_cart())
        self.assertIsNotNone(response['data']['cart'])
        self.assertNotIn('errors', response)
