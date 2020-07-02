from django.test import TestCase
from healthid.apps.sales.models import SaleReturnDetail


class SalesReturnDetailModelTest(TestCase):
    """Class for testing the model for sales return detail"""
    def test_string_representation(self):
        sales_return = SaleReturnDetail(return_reason="Expired Product")
        self.assertEqual(str(sales_return), sales_return.return_reason)
