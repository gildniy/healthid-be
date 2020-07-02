from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.business import (authentic_business,
                                                   update_business,
                                                   delete_business,
                                                   missing_business_email,
                                                   missing_trading_name,
                                                   missing_address_line_1,
                                                   missing_city,
                                                   missing_phone_number
                                                   )

from healthid.utils.messages.business_responses import BUSINESS_ERROR_RESPONSES
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.tests.factories import BusinessFactory


class GraphQLTestCase(BaseConfiguration):

    def test_create_business(self):
        """Test that a business can be created."""
        response = self.query_with_token(
            self.access_token_master, authentic_business)
        self.assertIn('data', response)

    def test_create_business_without_email(self):
        """Test failure to create a business without an email."""
        response = self.query_with_token(
            self.access_token_master, missing_business_email)
        self.assertEqual(response['errors'][0]['message'],
                         ERROR_RESPONSES[
                             "invalid_field_error"].format("email"))

    def test_create_business_without_trading_name(self):
        """Test failure to create a business without a trading name."""
        response = self.query_with_token(
            self.access_token_master, missing_trading_name)
        self.assertEqual(response['errors'][0]['message'],
                         BUSINESS_ERROR_RESPONSES["business_names_validation"])

    def test_create_business_without_address_line_1(self):
        """Test failure to create a business without address line 1."""
        response = self.query_with_token(
            self.access_token_master, missing_address_line_1)
        self.assertEqual(response['errors'][0]['message'],
                         BUSINESS_ERROR_RESPONSES["invalid_address1_error"])

    def test_create_business_without_city(self):
        """Test that a business can't be created without a city."""
        response = self.query_with_token(
            self.access_token_master, missing_city)
        self.assertEqual(response['errors'][0]['message'],
                         BUSINESS_ERROR_RESPONSES["blank_city_and_or_country"])

    def test_create_business_without_phone_number(self):
        """Test that a business can't be created without a city."""
        response = self.query_with_token(
            self.access_token_master, missing_phone_number)
        self.assertEqual(response['errors'][0]['message'],
                         ERROR_RESPONSES[
                             "required_field"].format("Phone number"))

    def test_update_business(self):
        """Test that a business can be updated."""
        response = self.query_with_token(self.access_token_master,
                                         update_business(self.business.id))
        self.assertIn('data', response)

    def test_update_business_you_are_not_assigned_to(self):
        """Test that you can't update a business you aren't assigned."""
        business = BusinessFactory()
        response = self.query_with_token(self.access_token_master,
                                         update_business(business.id))
        self.assertEqual(response['errors'][0]['message'], ERROR_RESPONSES[
            "update_error"])

    def test_delete_business(self):
        """Test that a business can be deleted."""
        business = BusinessFactory()
        response = self.query_with_token(self.access_token_master,
                                         delete_business(business.id))
        self.assertIn('data', response)
