from healthid.tests.products.test_create_product import TestCreateProduct
from healthid.tests.test_fixtures.products import (
    product_search_query,
    generalised_product_search_query,
    product_filter_pagination_query
)

from healthid.tests.test_fixtures.orders import (
    supplier_autofill_query
)

from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES


class TestFilterProducts(TestCreateProduct):
    def test_empty_search_string(self):
        "method that tests empty user input"
        search_term = ""
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))
        self.assertIn('errors', response)
        self.assertEquals(response['errors'][0]['message'],
                          PRODUCTS_ERROR_RESPONSES[
            "invalid_search_key"])

    def test_return_of_supplier_autofill(self):
        response = self.query_with_token(
            self.access_token, supplier_autofill_query)
        self.assertNotIn('errors', response)

    def test_return_search_result(self):
        "method that tests correct search result is returned"
        search_term = "pan"
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))
        self.assertNotIn('errors', response)
    
    def test_filter_pagination(self):
        "method that tests correctly that the returned result is paginated"
        search_term = "pan"
        response = self.query_with_token(
            self.access_token,product_filter_pagination_query.format(
                search_term=search_term))
        self.assertNotIn('errors', response)
        self.assertEquals(len(response['data']['filterProducts']['edges']),1)
            
    def test_return_search_result_when_product_does_not_contain_upc(self):
        "method that tests correct search result is returned"
        search_term = "pan"
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))
        self.assertNotIn('errors', response)
        self.assertEquals(response['data']['filterProducts']['edges']
                          [0]['node']['upc'],
                          None)
                        
    def test_return_search_result_when_product_contain_upc(self):
        "method that tests correct search result is returned"
        search_term = "Pizza"
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))
        self.assertNotIn('errors', response)
        self.assertEquals(response['data']['filterProducts']['edges']
                          [0]['node']['upc'],
                          'gdhmnkvu7738ndn')

    def test_return_search_result_given_global_upc(self):
        """
        method that tests correct search result is returned
        when provided a global upc
        """
        search_term = "gdhmnkvu7738ndn"
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))
        self.assertNotIn('errors', response)
        self.assertEquals(response['data']['filterProducts']['edges']
                          [0]['node']['productName'],
                          'Pizza')
        self.assertEquals(response['data']['filterProducts']['edges']
                          [0]['node']['upc'],
                          'gdhmnkvu7738ndn')

    def test_product_if_given_global_upc_does_not_exists(self):
        "method that tests when there is no product with the global upc passed"
        search_term = "rgdhmnkvu7738"
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))
        self.assertIn('errors', response)

    def test_nonexistent_product(self):
        "method that tests a product that does not exist"
        search_term = "dry"
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))

        self.assertIn('errors', response)
        self.assertEquals(response['errors'][0]['message'],
                          PRODUCTS_ERROR_RESPONSES[
            "inexistent_product_query"])

    def test_general_productname_search(self):
        "tests the return of an existing product using the "
        "generalised product search query and partial product name"
        search_term = "Cod"
        response = self.query_with_token(
            self.access_token, generalised_product_search_query.format(
                search_term=search_term))
        self.assertEquals(response['data']['products'][0]['productName'],
                          'Cod Liver Oil')

    def test_general_product_search_by_brand(self):
        "tests the return of an existing product using the "
        "generalised product search query and partial brand description"
        search_term = "maz"
        response = self.query_with_token(
            self.access_token, generalised_product_search_query.format(
                search_term=search_term))
        self.assertEquals(response['data']['products'][0]['productName'],
                          'Lozenge')

    def test_general_product_search_by_description(self):
        "tests the return of an existing product using the "
        "generalised product search query and partial product description"
        search_term = "oil"
        response = self.query_with_token(
            self.access_token, generalised_product_search_query.format(
                search_term=search_term))
        self.assertEquals(response['data']['products'][0]['productName'],
                          'Cod Liver Oil')

    def test_general_product_search_by_manufacturer(self):
        "tests the return of an existing product using the "
        "generalised product search query and partial manufacturer description"
        search_term = "GS"
        response = self.query_with_token(
            self.access_token, generalised_product_search_query.format(
                search_term=search_term))
        self.assertEquals(response['data']['products'][0]['productName'],
                          'Cod Liver Oil')

    def test_general_product_search_by_category(self):
        "tests the return of existing products using the "
        "generalised product search query and product category"
        search_term = "Prescription"
        response = self.query_with_token(
            self.access_token, generalised_product_search_query.format(
                search_term=search_term))
        self.assertEquals(len(response['data']['products']), 4)

    def test_general_product_search_by_supplier(self):
        "tests the return of existing products using the "
        "generalised product search query and product's preferred supplier"
        search_term = "p"
        response = self.query_with_token(
            self.access_token, generalised_product_search_query.format(
                search_term=search_term))
        self.assertEquals(len(response['data']['products']), 4)

    def test_return_search_result_non_admin_users(self):
        "method that tests correct search result is returned"
        search_term = "pan"
        response = self.query_with_token(
            self.access_token, product_search_query.format(
                search_term=search_term))
        self.assertNotIn('errors', response)

    def test_general_empty_search(self):
        "tests the result of an invalid search item"
        search_term = "!!387837gcc79e7g@@#"
        response = self.query_with_token(
            self.access_token, generalised_product_search_query.format(
                search_term=search_term))
        self.assertEquals(len(response['data']['products']), 0)
