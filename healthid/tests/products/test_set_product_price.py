from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import (
    set_price_string, set_markup_string, set_nothing_string
)
from healthid.utils.messages.products_responses import\
    PRODUCTS_SUCCESS_RESPONSES, PRODUCTS_ERROR_RESPONSES


class TestSetProductPriceTestCase(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.product_id1 = self.create_product(product_name='Poison').id
        self.product_id2 = self.create_product(product_name='product').id
    data = {
        'markup': 28,
        'product_ids': '[]',
        'sales_price': 20.32
    }

    def test_set_product_prices_automatically(self):
        self.data['product_ids'] = f'[{self.product_id1}, {self.product_id2}]'
        response = self.query_with_token(self.access_token_master,
                                         set_markup_string.format(**self.data))
        self.assertEqual(PRODUCTS_SUCCESS_RESPONSES["set_price_success"].format(
            key="markup", number=2, value=self.data['markup']),
            response['data']['updatePrice']['message'])

    def test_set_product_prices_manually(self):
        self.data['product_ids'] = f'[{self.product_id1}, {self.product_id2}]'
        response = self.query_with_token(self.access_token_master,
                                         set_price_string.format(**self.data))
        self.assertEqual(PRODUCTS_SUCCESS_RESPONSES["set_price_success"].format(
            key="sales price", number=2, value=self.data['sales_price']),
            response['data']['updatePrice']['message']
        )

    def test_update_price_without_any_choice(self):
        self.data['product_ids'] = f'[{self.product_id1}, {self.product_id2}]'
        response = self.query_with_token(self.access_token_master,
                                         set_nothing_string.format(**self.data))
        self.assertEqual(PRODUCTS_ERROR_RESPONSES["update_price_error"],
                         response["errors"][0]["message"])
