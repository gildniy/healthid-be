from healthid.apps.preference.models import Vat
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.vat import (set_vat,
                                              query_vat_by_id,
                                              query_vat_by_wrong_id)


class VatTestCase(BaseConfiguration):

    def setUp(self):
        super().setUp()
        self.new_vat = Vat(
            id="t1234qwe", rate=22.5)
        self.new_vat.save()

    def test_vat_model(self):
        self.rate = self.new_vat.rate
        self.assertEqual(self.rate, 22.5)

    def test_query_vat_by_id(self):
        response = self.query_with_token(
            self.access_token_master, query_vat_by_id)
        self.assertNotIn('errors', response)

    def test_query_vat_by_wrong_id(self):
        response = self.query_with_token(
            self.access_token_master, query_vat_by_wrong_id)
        self.assertIn('errors', response)

    def test_set_vat(self):
        response = self.query_with_token(
            self.access_token_master, set_vat(self.preference.id)
        )
        self.assertNotIn('errors', response)
