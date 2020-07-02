from healthid.tests.base_config import BaseConfiguration
from healthid.tests.factories import (
    CustomerCreditFactory, CurrencyFactory, CustomerFactory)
from healthid.tests.test_fixtures.wallet import create_customer_credit
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.customer_responses import CUSTOMER_ERROR_RESPONSES


class TestCustomerCredit(BaseConfiguration):
    """
        Tests creating a customer credit account
    """

    def setUp(self):
        super(TestCustomerCredit, self).setUp()

        self.currency = CurrencyFactory()
        self.customer = CustomerFactory()

        self.account = {
            "customer_id": self.customer.id
        }

    def test_create_customer_credit(self):
        response = self.query_with_token(
            self.access_token, create_customer_credit.format(**self.account))

        message = SUCCESS_RESPONSES[
            "creation_success"].format("Customer's credit account")

        self.assertEqual(
            message, response['data']['createCustomerCredit']['message'])
        self.assertNotIn("errors", response)

    def test_create_customer_credit_already_exists(self):
        _ = CustomerCreditFactory(
            customer=self.customer, credit_currency=self.currency)

        response = self.query_with_token(
            self.access_token, create_customer_credit.format(**self.account))

        message = CUSTOMER_ERROR_RESPONSES[
            "customer_credit_double_creation_error"]

        self.assertEqual(
            message, response['errors'][0]['message'])
