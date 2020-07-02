from healthid.tests.sales.promotion_base import TestPromotion
from healthid.tests.test_fixtures.sales import \
    generate_custom_near_expire_promos


class TestNearExpirePromotion(TestPromotion):
    def setUp(self):
        super().setUp()
        self.promotion_data = {
            "product_id": self.product.id,
            "promotion_id": self.promotion.id,
            "apply_months": 5
        }

    def test_admin_can_generate_custom_discount(self):
        response = self.query_with_token(
            self.access_token_master,
            generate_custom_near_expire_promos.format(**self.promotion_data))
        self.assertIn(
            "success",
            response["data"]["createCustomNearExpirePromotion"])
        self.assertNotIn('errors', response)

    def test_generate_custom_discount_with_invalid_product_id(self):
        self.promotion_data['product_id'] = 123456780
        response = self.query_with_token(
            self.access_token_master,
            generate_custom_near_expire_promos.format(**self.promotion_data))
        self.assertNotIn("success", response)
        self.assertIn("errors", response)
        self.assertIn("Product with id 123456780 does not exist.",
                      response['errors'][0]['message'])

    def test_generate_custom_discount_with_invalid_promotion_id(self):
        self.promotion_data['promotion_id'] = 123456780
        response = self.query_with_token(
            self.access_token_master,
            generate_custom_near_expire_promos.format(**self.promotion_data))
        self.assertNotIn("success", response)
        self.assertIn("errors", response)
        self.assertIn("Promotion with id 123456780 does not exist.",
                      response['errors'][0]['message'])

    def test_generate_custom_discount_with_invalid_months(self):
        self.promotion_data['apply_months'] = 13
        response = self.query_with_token(
            self.access_token_master,
            generate_custom_near_expire_promos.format(**self.promotion_data))
        self.assertNotIn("success", response)
        self.assertIn("errors", response)
        self.assertIn("Months must be between 1 and 12",
                      response['errors'][0]['message'])
