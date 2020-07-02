from healthid.apps.orders.models import BarcodeScan
from healthid.apps.preference.models import OutletPreference
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.barcode_scans import barcode_scan
from healthid.utils.app_utils.database import get_model_object


class TestBarcodeScans(BaseConfiguration):
    """BarcodeScan tests."""

    def setUp(self):
        super().setUp()
        self.order = self.create_order(closed=True)
        self.barcode_object_data = {
            'scanned_number': '123456789012',
            'batch_info': self.batch_info,
            'outlet': self.outlet,
            'product': self.product,
            'count': 1,
            'order': self.order
        }
        outlet = self.outlet
        preference = get_model_object(OutletPreference, 'outlet_id', outlet.id)
        setattr(preference, 'barcode_preference', True)
        preference.save()

        self.barcode_query_data = {
            'scanned_number': '123456789012',
            'batch_id': self.batch_info.id,
            'outlet_id': outlet.id,
            'product_id': self.product.id,
            'count': 1,
        }

    def test_barcode_scan_string_representation(self):
        """Test the representing our model as a string."""
        self.barcode_object_data['order'] = self.create_order(closed=True)
        self.barcode_object_data.pop('product')
        self.barcode_object_data.pop('outlet')
        scan = BarcodeScan.objects.create(**self.barcode_object_data)
        self.assertTrue(str(scan).startswith('Order NO:'))

    def test_record_scan(self):
        """Test that scanned data is properly recorded."""
        self.barcode_query_data['order_id'] = self.create_order(closed=True).id
        response = self.query_with_token(
            self.access_token, barcode_scan.format(
                **self.barcode_query_data
            )
        )
        self.assertNotIn('errors', response)

    def test_record_scan_is_not_saved_when_order_is_open(self):
        """Test that scan is rejected when the order is not closed."""
        self.barcode_query_data['order_id'] = \
            self.create_order(closed=False).id
        response = self.query_with_token(
            self.access_token, barcode_scan.format(
                **self.barcode_query_data
            )
        )
        self.assertIn('errors', response)
