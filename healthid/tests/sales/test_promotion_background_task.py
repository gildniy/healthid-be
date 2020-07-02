from django.test import TestCase
from mock import patch
from django.core.management import call_command
from healthid.utils.product_utils.product_expiry import \
    check_for_expiry_products
from healthid.apps.products.models import BatchInfo
from datetime import datetime, timedelta


class TestBackgroundTasks(TestCase):
    def setUp(self):
        call_command('loaddata', 'healthid/fixtures/role_data')
        call_command('loaddata', 'healthid/fixtures/authentication')
        call_command('loaddata', 'healthid/fixtures/promotion')

    def change_batch_expiry_date(self, days):
        batches = BatchInfo.objects.all()
        for batch in batches:
            batch.expiry_date = datetime.today().date() + timedelta(days=days)
            batch.save()

    @patch('healthid.utils.product_utils.product_expiry.create_promotion')
    def test_create_promotion_for_six_months_near_expiry_products(self, mock):
        self.change_batch_expiry_date(170)
        check_for_expiry_products()
        self.assertEqual(mock.call_count, 1)

    @patch('healthid.utils.product_utils.product_expiry.create_promotion')
    def test_create_promotion_for_three_month_near_expiry_products(self, mock):
        self.change_batch_expiry_date(70)
        check_for_expiry_products()
        self.assertEqual(mock.call_count, 1)

    @patch('healthid.utils.product_utils.product_expiry.create_promotion')
    def test_create_promotion_for_one_month_near_expiry_products(self, mock):
        self.change_batch_expiry_date(25)
        check_for_expiry_products()
        self.assertEqual(mock.call_count, 1)
