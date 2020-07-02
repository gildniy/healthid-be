from healthid.apps.preference.models import Timezone
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.preferences import (timezone_query,
                                                      timezones_query,
                                                      update_timezone_query,
                                                      wrong_timezone,
                                                      wrong_query
                                                      )


class TimezoneTestCase(BaseConfiguration):

    def setUp(self):
        super().setUp()
        self.new_timezone = Timezone(
            id="285461788", name="America/Vancouver",
            time_zone="(GMT-08:00) Pacific Time - Vancouver")
        self.new_timezone.save()

    def test_query(self):
        response = self.query_with_token(
            self.access_token_master, timezone_query % (self.outlet.id))
        self.assertIn('data', response)

    def test_get_all_timezones(self):
        response = self.query_with_token(
            self.access_token_master, timezones_query)
        self.assertIn('data', response)

    def test_timezone_model(self):
        self.assertEqual(str(self.timezone), "(GMT+01:00) Lagos")

    def test_update_timezone(self):
        response = self.query_with_token(
            self.access_token_master,
            update_timezone_query % (self.preference.id))
        self.assertIn('data', response)

    def test_wrong_timezone(self):
        response = self.query_with_token(
            self.access_token_master, wrong_timezone % (self.outlet.id))
        self.assertIn('errors', response)

    def test_wrong_query(self):
        response = self.query_with_token(
            self.access_token_master, wrong_query)
        self.assertIn('errors', response)
