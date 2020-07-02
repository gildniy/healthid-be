from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.wallet import (
    customer_id_store_credit_query,
    store_credit_query_all,
    customer_credit_pagination_query,
    customer_credit_invalid_argument)
from healthid.tests.factories import (
    CustomerCreditFactory, CustomerFactory, CurrencyFactory)


class TestQueryCustomerCredit(BaseConfiguration):
    """ Test querying customer credit"""

    def setUp(self):
        super(TestQueryCustomerCredit, self).setUp()
        self.customer = CustomerFactory()
        self.currency = CurrencyFactory()
        self.customer_credit = CustomerCreditFactory(
            customer=self.customer, credit_currency=self.currency)

    def test_fetch_all_credit_account(self):
        """ Test getting all store credit accounts. """

        response = self.query_with_token(
            self.access_token, store_credit_query_all
        )

        expected_credit = 0.0
        self.assertEqual(
            expected_credit,
            response['data']['customerCredits'][0]['storeCredit'])

    def test_query_store_credit_by_customer_id(self):
        """ Test fetching store credit using customerId. """
        expected_store_credit = 0.0
        response = self.query_with_token(
            self.access_token,
            customer_id_store_credit_query.format(
                customer_id=self.customer.id
            )
        )
        self.assertEqual(
            expected_store_credit,
            response['data']['customerCredit']['storeCredit'])

    def test_store_credit_pagination(self):
        """ Test fetching store credits using pagination. """
        response = self.query_with_token(
            self.access_token, customer_credit_pagination_query.format(1, 1))

        expected_credit = 0.0
        self.assertEqual(
            expected_credit,
            response['data']['customerCredits'][0]['storeCredit'])

    def test_no_store_credit_account_for_customer(self):
        """ Test when the store credits account is not found for customer. """
        response = self.query_with_token(
            self.access_token,
            customer_id_store_credit_query.format(customer_id=2)
        )
        self.assertEqual(None, response['data']['customerCredit'])

    def test_invalid_arguments(self):
        """ Test when the store credits account is not found for customer. """
        response = self.query_with_token(
            self.access_token,
            customer_credit_invalid_argument.format('s', "invalidArg:2")
        )
        self.assertFalse(len(response['errors'][0]['message']) < 1)
