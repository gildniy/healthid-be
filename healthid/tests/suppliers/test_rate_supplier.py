from healthid.tests.base_config import BaseConfiguration
from healthid.apps.orders.models.suppliers import SupplierRating
from healthid.tests.factories import SupplierRatingFactory
from healthid.tests.test_fixtures.suppliers\
    import rate_supplier, get_supplier_rating
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES


class TestRateSupplier(BaseConfiguration):
    def setUp(self):
        super(TestRateSupplier, self).setUp()
        self.suppliers_rating_factory = SupplierRatingFactory()

    def test_rate_supplier(self):
        data = {
            "supplier_id": self.supplier.id,
            "delivery_promptness": 1,
            "service_quality": 1
        }
        response = self.query_with_token(
            self.access_token,
            rate_supplier.format(**data))
        expected_message = SUCCESS_RESPONSES[
            "creation_success"].format("Supplier's rating")
        self.assertEqual(
            expected_message,
            response["data"]["rateSupplier"]["message"])
        self.assertNotIn("errors", response)

    def test_rate_supplier_with_wrong_delivery_promptness(self):
        data = {
            "supplier_id": self.supplier.id,
            "delivery_promptness": 2,
            "service_quality": 1
        }
        expected_message = ORDERS_ERROR_RESPONSES["invalid_rating"].format(
            "delivery_promptness", 1)
        response = self.query_with_token(
            self.access_token,
            rate_supplier.format(**data))
        self.assertEqual(expected_message, response["errors"][0]["message"])
        self.assertIn("errors", response)

    def test_rate_supplier_with_wrong_service_quality(self):
        data = {
            "supplier_id": self.supplier.id,
            "delivery_promptness": 1,
            "service_quality": 5
        }
        expected_message = ORDERS_ERROR_RESPONSES["invalid_rating"].format(
            "service_quality", 4)
        response = self.query_with_token(
            self.access_token,
            rate_supplier.format(**data))
        self.assertEqual(expected_message, response["errors"][0]["message"])
        self.assertIn("errors", response)

    def test_get_supplier_rating(self):
        SupplierRating.objects.create(supplier_id=self.supplier.id, rating=4)
        SupplierRating.objects.create(supplier_id=self.supplier.id, rating=1)
        data = {
            "supplier_id": self.supplier.id
        }
        response = self.query_with_token(
            self.access_token,
            get_supplier_rating.format(**data))
        self.assertEqual(response["data"]["supplierRating"], 2.5)

    def test_get_unerated_supplier_rating(self):
        data = {
            "supplier_id": self.supplier.id
        }
        response = self.query_with_token(
            self.access_token,
            get_supplier_rating.format(**data))
        self.assertEqual(response["data"]["supplierRating"], 0)
