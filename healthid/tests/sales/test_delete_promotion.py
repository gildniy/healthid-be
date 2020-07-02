from healthid.tests.test_fixtures.sales import delete_promotion
from healthid.tests.sales.promotion_base import TestPromotion
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


class TestDeletePromotion(TestPromotion):
    def test_admin_can_delete_a_promotion(self):
        response = self.query_with_token(self.access_token_master,
                                         delete_promotion(self.promotion.id))
        self.assertIn("success", response["data"]["deletePromotion"])
        self.assertNotIn('errors', response)

    def test_cannot_delete_promotion_for_outlet_you_arent_active_in(self):
        response = self.query_with_token(self.second_master_admin_token,
                                         delete_promotion(self.promotion.id))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(
            response['errors'][0]['message'],
            OUTLET_ERROR_RESPONSES["logged_in_user_not_active_in_outlet"])

    def test_cannot_delete_promotion_that_doesnt_exist(self):
        promotion_id = self.promotion.id
        self.query_with_token(self.access_token_master,
                              delete_promotion(promotion_id))
        response = self.query_with_token(self.access_token_master,
                                         delete_promotion(promotion_id))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES[
                             "inexistent_promotion"].format(promotion_id))

    def test_cannot_delete_promotion_when_unauthenticated(self):
        response = self.query_with_token('',
                                         delete_promotion(self.promotion.id))
        self.assertIsNotNone(response['errors'])
