from healthid.tests.test_fixtures.sales import approve_promotion
from healthid.tests.sales.promotion_base import TestPromotion
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES


class TestApprovePromotion(TestPromotion):
    def setUp(self):
        super().setUp()
        self.promotion.is_approved = False
        self.promotion.save()

    def test_admin_can_approve_a_promotion(self):
        response = self.query_with_token(self.access_token_master,
                                         approve_promotion(self.promotion.id))
        self.assertIn("success", response["data"]["approvePromotion"])
        self.assertNotIn('errors', response)

    def test_cannot_approve_promotion_for_outlet_you_arent_active_in(self):
        response = self.query_with_token(self.second_master_admin_token,
                                         approve_promotion(self.promotion.id))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(
            response['errors'][0]['message'],
            OUTLET_ERROR_RESPONSES["logged_in_user_not_active_in_outlet"])

    def test_cannot_approve_promotion_that_doesnt_exist(self):
        response = self.query_with_token(self.access_token_master,
                                         approve_promotion('iewi1237011'))
        self.assertIsNotNone(response['errors'])
        self.assertEqual(response['errors'][0]['message'],
                         SALES_ERROR_RESPONSES[
                             "inexistent_promotion"].format("iewi1237011"))

    def test_cannot_approve_promotion_when_unauthenticated(self):
        response = self.query_with_token('',
                                         approve_promotion(self.promotion.id))
        self.assertIsNotNone(response['errors'])
