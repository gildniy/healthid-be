from dateutil.relativedelta import relativedelta

from django.utils import timezone

from healthid.apps.preference.models import OutletPreference
from healthid.apps.sales.sales_velocity import SalesVelocity
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.sales import sales_velocity_query
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.sales_responses import (
    SALES_ERROR_RESPONSES)


class TestSalesVelocity(BaseConfiguration):
    def setUp(self):
        super().setUp()

        self.velocity_data = {
            "product_id": self.product.id,
            "outlet_id": self.outlet.id
        }
        outlet_preference = get_model_object(
            OutletPreference, 'outlet_id', self.outlet.id)
        self.sales_velocity = outlet_preference.sales_velocity

    def test_weekly_sales_below_minimum(self):
        """
        Tests when count of weeks with sales
        is below the minimum set in outlet preferences
        """
        message = SALES_ERROR_RESPONSES['default_velocity']
        response = self.query_with_token(
            self.access_token,
            sales_velocity_query.format(**self.velocity_data))

        self.assertNotIn('errors', response)
        self.assertEqual(
            self.sales_velocity,
            response['data']['salesVelocity']['defaultSalesVelocity'])
        self.assertIn(
            'calculatedSalesVelocity',
            response['data']['salesVelocity'])
        self.assertEqual(
            message,
            response['data']['salesVelocity']['message'])

    def test_weekly_sales_method(self):
        self.assertEqual(
            SalesVelocity(**self.velocity_data).weekly_sales(
                weeks_count=2), [0, 0])

    def test_get_sales_for_period_method(self):
        self.assertEqual(
            SalesVelocity(
                **self.velocity_data).get_sales_for_period(
                current_date=timezone.now(),
                earlier_date=timezone.now() + relativedelta(weeks=-1)),
            [None])
