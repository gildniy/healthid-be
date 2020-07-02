from faker import Faker

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.wallet import (
    edit_credit)
from healthid.utils.messages.common_responses import (
    SUCCESS_RESPONSES)
from healthid.utils.messages.customer_responses import CUSTOMER_ERROR_RESPONSES
from healthid.tests.factories import CustomerCreditFactory


fake = Faker()


class TestCustomerCredit(BaseConfiguration):
    """Tests updating customer credit."""

    def setUp(self):
        super().setUp()
        self.customer_credit = CustomerCreditFactory.create(
            store_credit=0.0
        )

        self.credit_data = {
            "customer_id": self.customer_credit.customer_id,
            "store_credit": fake.random_int(min=1)
        }

    def test_update_customer_credit(self):
        response = self.query_with_token(
            self.access_token_master, edit_credit.format(
                **self.credit_data)
        )
        message = SUCCESS_RESPONSES[
            "update_success"].format("Credit")
        self.assertEqual(
            response['data']['editCustomerWallet']['message'], message)

    def test_update_customer_credit_with_negative_number(self):
        self.credit_data['store_credit'] = fake.random_int(min=-10000, max=-1)
        response = self.query_with_token(
            self.access_token_master, edit_credit.format(
                **self.credit_data)
        )
        message = CUSTOMER_ERROR_RESPONSES['wrong_amount']
        self.assertEqual(
            response['errors'][0]['message'], message)

    def test_update_customer_credit_with_amount(self):
        self.credit_data['store_credit'] = 2000.0
        response = self.query_with_token(
            self.access_token_master,
            edit_credit.format(
                **self.credit_data)
        )
        self.assertEqual(
            response['data']['editCustomerWallet']['customer']
            ['storeCredit'], 2000.0)
