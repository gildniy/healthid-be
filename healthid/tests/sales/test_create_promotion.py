from healthid.tests.sales.promotion_base import TestPromotion
from healthid.tests.test_fixtures.sales import (create_promotion,
                                                create_promotion_type)
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


class TestCreatePromotion(TestPromotion):
    def setUp(self):
        super().setUp()

    def test_manager_can_create_a_promotion(self):
        self.promotion_data['title'] = 'new promo'
        response = self.query_with_token(self.access_token_master,
                                         create_promotion(self.promotion_data))
        self.assertIn('success', response['data']['createPromotion'])
        self.assertNotIn('errors', response)

    def test_cannot_create_promotion_without_required_fields(self):
        self.promotion_data['title'] = ''
        response = self.query_with_token(self.access_token_master,
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'title is required.')

    def test_cannot_create_promotion_with_same_title(self):
        response = self.query_with_token(self.access_token_master,
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         ERROR_RESPONSES[
                         "duplication_error"].format(
                               "Promotion with title another promo"))

    def test_only_manager_admin_can_create_promotion(self):
        self.business.user = self.user
        response = self.query_with_token(self.access_token,
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])

    def test_cannot_create_promotion_for_outlet_you_arent_active_in(self):
        response = self.query_with_token(self.second_master_admin_token,
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(
            response['errors'][0]['message'],
            OUTLET_ERROR_RESPONSES["logged_in_user_not_active_in_outlet"])

    def test_cannot_create_promotion_when_unauthenticated(self):
        response = self.query_with_token('',
                                         create_promotion(self.promotion_data))
        self.assertIsNotNone(response['errors'])

    def test_manager_can_create_a_promotion_type(self):
        response = self.query_with_token(self.access_token_master,
                                         create_promotion_type('Monthly'))
        self.assertIn('success', response['data']['createPromotionType'])
        self.assertNotIn('errors', response)

    def test_cannot_create_promotion_type_without_required_fields(self):
        response = self.query_with_token(self.access_token_master,
                                         create_promotion_type(''))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES["promotion_type_error"])

    def test_cannot_create_promotion_type_with_same_name(self):
        self.query_with_token(self.access_token_master,
                              create_promotion_type('Monthly'))
        response = self.query_with_token(self.access_token_master,
                                         create_promotion_type('Monthly'))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         ERROR_RESPONSES[
                         "duplication_error"].format(
                               "PromotionType with name Monthly"))
