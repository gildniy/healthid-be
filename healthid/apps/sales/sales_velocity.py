""" Contains business logic for calculating sales velocity."""
import collections
from dateutil.relativedelta import relativedelta

from django.db.models import Sum
from django.utils import timezone

from healthid.apps.preference.models import OutletPreference
from healthid.apps.sales.models import SaleDetail
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.sales_responses import (
    SALES_ERROR_RESPONSES, SALES_SUCCESS_RESPONSES)


class SalesVelocity():
    """
    Class contains methods for calculating
    sales velocity and checking inventory
    levels
    """
    def __init__(self, product_id, outlet_id, weeks_count=4):
        super(SalesVelocity, self).__init__()
        self.outlet_preferences = get_model_object(
            OutletPreference, 'outlet_id', outlet_id)
        self.minimum_weeks = self.outlet_preferences.minimum_weeks_for_sales_velocity  # noqa
        self.reorder_max = self.outlet_preferences.reorder_max
        self.reorder_point = self.outlet_preferences.reorder_point
        self.product_id = product_id
        self.outlet_id = outlet_id
        self.weeks_count = weeks_count
        self.message = SALES_SUCCESS_RESPONSES['calculated_velocity']

    def weekly_sales(self, weeks_count):
        """
        Args:
            weeks_count (int) how many weeks of sales
                that are to be queried.
        Returns an array of sales for a product.
        The values are for a sum of n weeks back
            starting from the day the request is made
        """
        today = timezone.now()

        week_sales = []
        initial_weeks_count = 0

        while initial_weeks_count < weeks_count:
            current_date = today + relativedelta(
                weeks=-(initial_weeks_count+1))
            earlier_date = today + relativedelta(
                weeks=-(initial_weeks_count+2))
            week_sale = self.get_sales_for_period(
                current_date, earlier_date)
            week_sales.append(week_sale[0])
            initial_weeks_count += 1

        week_sales = [(
            lambda week_sale: 0 if week_sale is None else week_sale)(
            week_sale) for week_sale in week_sales]

        return week_sales

    def get_sales_for_period(self, current_date, earlier_date):
        """
        Get total sales for a specific period
        Args:
            current_date (date) When the period starts going back
            earlier_date (date) When the period ends going forward
        Returns:
            A list containing total sales, which
            can be an int or None
        """
        period_sales = SaleDetail.objects.filter(
            product_id=self.product_id,
            created_at__gte=earlier_date,
            created_at__lte=current_date).aggregate(
            Sum('quantity')).values()
        return list(period_sales)

    def velocity_calculator(self):
        """
        Calculates sales velocity
        Returns:
             sales_velocity(float) if calculation is successful or
             a GraphQLError is the number of weekly sales provided
             are less than the minimum_weeks
        """
        week_sales = self.weekly_sales(self.weeks_count)
        weeks_count = len(week_sales)

        total_sales = sum(week_sales)

        calculated_sales_velocity = round(total_sales/weeks_count, 2)
        default_sales_velocity = self.outlet_preferences.sales_velocity

        if all(week_sales[self.minimum_weeks-1:len(week_sales)]) == 0:
            self.message = SALES_ERROR_RESPONSES['default_velocity']

        OutputVelocity = collections.namedtuple(
            'OutputVelocity',
            'default_sales_velocity calculated_sales_velocity message')

        sales_velocity = OutputVelocity(
            default_sales_velocity=default_sales_velocity,
            calculated_sales_velocity=calculated_sales_velocity,
            message=self.message)

        return sales_velocity
