from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.customers import (create_customer)
from healthid.utils.messages.common_responses import\
    SUCCESS_RESPONSES, ERROR_RESPONSES
from healthid.utils.messages.customer_responses import CUSTOMER_ERROR_RESPONSES


class TestCustomerCreation(BaseConfiguration):
    def test_create_customer(self):
        """Test method for creating a customer"""
        response = self.query_with_token(
            self.access_token,
            create_customer.format(**self.create_customer_data))
        expected_message = SUCCESS_RESPONSES[
            "creation_success"].format("Customer")
        self.assertEqual(
            expected_message,
            response["data"]["createCustomer"]["message"])
        self.assertIn("wallet", response["data"]["createCustomer"]["customer"])
        self.assertNotIn("errors", response)

    def test_create_customer_invalid_firstname(self):
        """Test method for creating a customer with invalid firstname"""
        self.create_customer_data['first_name'] = "H@#@qwer"
        response = self.query_with_token(
            self.access_token,
            create_customer.format(**self.create_customer_data))
        expected_message = "Special characters not allowed"
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_customer_invalid_email(self):
        """Test method for creating a customer with invalid email"""
        self.create_customer_data['email'] = "talktohabibgmail.com"
        response = self.query_with_token(
            self.access_token,
            create_customer.format(**self.create_customer_data))
        expected_message = ERROR_RESPONSES[
            "invalid_field_error"].format("email")
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_customer_firstname_as_empty_string(self):
        """Test method for creating a customer with invalid firstname"""
        self.create_customer_data['first_name'] = ""
        response = self.query_with_token(
            self.access_token,
            create_customer.format(**self.create_customer_data))
        expected_message = CUSTOMER_ERROR_RESPONSES[
            "first_name_error"].format("first_name")
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_customer_mobileNumber_as_empty_string(self):
        """Test method for creating a customer with invalid mobileNumber"""
        self.create_customer_data['primary_mobile_number'] = "23456"
        response = self.query_with_token(
            self.access_token,
            create_customer.format(**self.create_customer_data))
        expected_message = ERROR_RESPONSES[
            "invalid_field_error"
        ].format("mobile number (ex. +2346787646)")
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])
