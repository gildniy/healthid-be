from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import\
    (all_products_default_pagination, all_proposed_products_default_pagination,
     all_approved_products_default_pagination)


class TestProductPagination(BaseConfiguration):
    """
    class handles tests for products queries with pagination
    """

    def test_retrieve_all_products_default_pagination(self):
        response = self.query_with_token(
            self.access_token_master, all_products_default_pagination)
        self.assertEqual(response["data"]["totalProductsPagesCount"], 1)

    def test_retrieve_proposed_products_default_pagination(self):
        response = self.query_with_token(
            self.access_token_master, all_proposed_products_default_pagination)
        self.assertEqual(response["data"]["totalProductsPagesCount"], 1)

    def test_retrieve_approved_products_default_pagination(self):
        response = self.query_with_token(
            self.access_token_master, all_approved_products_default_pagination)
        self.assertEqual(response["data"]["totalProductsPagesCount"], 1)
