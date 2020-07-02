from healthid.apps.preference.models import Currency
from healthid.tests.base_config import BaseConfiguration


class CurrencyBaseTest(BaseConfiguration):

    def create_currency(self):

        self.currency = Currency(
            name="Mozambican Metical",
            symbol="MTn",
            symbol_native="MTn",
            decimal_digits=2,
            rounding=0,
            code="MZN",
            name_plural="Mozambican meticals",
            outlet_id=self.outlet.id
        )
        self.currency.save()
        return self.currency
