from healthid.apps.preference.models import Currency
from healthid.tests.preferences.currency_base import CurrencyBaseTest
from healthid.tests.test_fixtures.currency import (get_currencies,
                                                   get_currency,
                                                   get_wrong_currency,
                                                   set_currency,
                                                   set_existing_currency)


class CurrencyTest(CurrencyBaseTest):

    def test_set_currency(self):
        response = self.query_with_token(
            self.access_token_master, set_currency(self.preference.id)
        )
        self.assertIn('data', response)

    def test_set_same_currency(self):
        response = self.query_with_token(
            self.access_token_master,
            set_existing_currency(self.preference.id)
        )
        self.assertIn('data', response)

    def test_get_wrong_currency(self):
        response = self.query_with_token(
            self.access_token_master, get_wrong_currency()
        )
        self.assertIn('data', response)

    def test_get_currencies(self):
        response = self.query_with_token(
            self.access_token_master, get_currencies(),
        )
        self.assertIn('data', response)

    def test_get_currency(self):
        response = self.query_with_token(
            self.access_token_master, get_currency()
        )
        self.assertIn('data', response)

    def test_currency_model(self):
        currency = Currency()
        currency.name = "Euro"
        assert(str(currency) == 'Euro')
