from healthid.tests.sales.promotion_base import TestPromotion
from healthid.tests.test_fixtures.sales import update_promotion
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


class TestUpdatePromotion(TestPromotion):

    def test_admin_can_update_a_promotion(self):
        response = self.query_with_token(self.access_token_master,
                                         update_promotion(self.promotion.id,
                                                          'new promo'))
        self.assertIn("success", response["data"]["updatePromotion"])
        self.assertNotIn('errors', response)

    def test_only_admin_manager_can_update_promotion(self):
        self.business.user = self.user
        response = self.query_with_token(self.access_token,
                                         update_promotion(self.promotion.id,
                                                          'new promo'))
        self.assertIsNotNone(response['errors'])

    def test_cannot_update_promotion_for_outlet_you_arent_active_in(self):
        response = self.query_with_token(self.second_master_admin_token,
                                         update_promotion(self.promotion.id,
                                                          'new promo'))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(
            response['errors'][0]['message'],
            OUTLET_ERROR_RESPONSES["logged_in_user_not_active_in_outlet"])

    def test_cannot_update_promotion_that_doesnt_exist(self):
        response = self.query_with_token(self.access_token_master,
                                         update_promotion('agfgadg',
                                                          'new promo'))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES[
                             "inexistent_promotion"].format("agfgadg"))

    def test_cannot_update_promotion_with_empty_title(self):
        response = self.query_with_token(self.access_token_master,
                                         update_promotion(self.promotion.id,
                                                          ''))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         'title is required.')

    def test_cannot_update_promotion_with_existing_title(self):
        response = self.query_with_token(
            self.access_token_master, update_promotion(
                self.second_promotion.id, self.promotion.title))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         ERROR_RESPONSES[
                             "duplication_error"].format(
                             "Promotion with title my promo"))

    def test_cannot_update_promotion_when_unauthenticated(self):
        response = self.query_with_token('',
                                         update_promotion(self.promotion.id,
                                                          'new promo'))
        self.assertIsNotNone(response['errors'])
