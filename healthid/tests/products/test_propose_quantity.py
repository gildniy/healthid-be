from healthid.tests.base_config import BaseConfiguration
from healthid.apps.products.models import Quantity
from healthid.tests.test_fixtures.batch_quantity import (propose_quantity,
                                                         propose_quantity2,
                                                         approve_quantity)
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES


class TestProposeQuantity(BaseConfiguration):
    """
    Class that handles the test suite for proposing quantity
    """

    def setUp(self):
        """
        Setup class that runs before each test
        """
        super().setUp()
        self.data = {
            'batch_id': self.batch_info.id,
            'product_id': self.product.id
        }

    def test_quantity_model(self):
        """
        Test the quantity model
        """
        all_quantities = Quantity.objects.all()
        self.assertGreater(len(all_quantities), 0)

    def test_proposed_quantity(self):
        """
        Test proposing a quantity to a batch
        """
        response = self.query_with_token(
            self.access_token_master, propose_quantity.format(**self.data))
        self.assertIn("sent!", response['data']['proposedQuantity']
                      ['notification'])

    def test_pending_request(self):
        """
        Test that no new request is sent if there is a pending request
        """
        self.query_with_token(
            self.access_token_master, propose_quantity.format(**self.data))
        response = self.query_with_token(
            self.access_token_master, propose_quantity.format(**self.data))
        self.assertIn("pending request", response['errors'][0]['message'])

    def test_lists_do_not_match(self):
        """"
        Test for an error message if products and quantities lists do not match
        """
        response = self.query_with_token(
            self.access_token_master, propose_quantity2.format(**self.data))
        self.assertIn("do not match", response['errors'][0]['message'])

    def test_approve_proposed_quantity(self):
        """"
        Test method for approving a proposed quantity edit
        """
        self.query_with_token(
            self.access_token_master, propose_quantity.format(**self.data))
        self.data['value'] = 'true'
        response = self.query_with_token(
            self.access_token_master, approve_quantity.format(**self.data))
        self.assertIn("has been approved",
                      response['data']['approveQuantity']['message'])

    def test_decline_proposed_quantity(self):
        """"
        Test method for declining a proposed quantity edit
        """
        self.query_with_token(
            self.access_token_master, propose_quantity.format(**self.data))
        self.data['value'] = 'false'
        response = self.query_with_token(
            self.access_token_master, approve_quantity.format(**self.data))
        self.assertIn("has been declined",
                      response['data']['approveQuantity']['message'])

    def test_approve_product_with_no_proposal(self):
        """"
        Test method for validating product that has not been proposed
        """
        self.query_with_token(
            self.access_token_master, propose_quantity.format(**self.data))
        self.data['value'] = 'true'
        self.query_with_token(
            self.access_token_master, approve_quantity.format(**self.data))
        response = self.query_with_token(
            self.access_token_master, approve_quantity.format(**self.data))
        self.assertIn(
            PRODUCTS_ERROR_RESPONSES["inexistent_proposal_error"],
            response['errors'][0]['message'])
