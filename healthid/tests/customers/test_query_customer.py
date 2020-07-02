from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.customers import (
    customer_query_all, customer_search_query,
    customer_name_query, customer_number_query, customer_id_query,
    customer_query_paginated, customer_custom_query_paginated,
    customer_filter_paginated, customer_universal_query,
    customer_total_number_query)
from healthid.tests.factories import CustomerFactory


class TestQueryCustomer(BaseConfiguration):
    """Tests querying customer"""

    def setUp(self):
        super(TestQueryCustomer, self).setUp()
        self.customer_2 = CustomerFactory()

    def test_fetch_all_customers(self):
        """
        Tests fetching all customers when one or more has been created
        """
        response = self.query_with_token(
            self.access_token, customer_query_all)
        expected_name = self.customer_2.last_name
        self.assertNotIn('errors', response)
        self.assertIn('data', response)
        self.assertEqual(
            expected_name,
            response['data']['customers'][0]['lastName'])
    
    def test_universal_customer_query_for_name(self):
        """
        Tests fetching a customer's name using the universal search parameter
        """
        response = self.query_with_token(
            self.access_token,
            customer_universal_query.format(
                search_item=self.customer_2.first_name))
        self.assertEqual(
            self.customer_2.last_name,
            response['data']['customer'][0]['lastName'])

    def test_universal_customer_query_for_phonenumber(self):
        """
        Tests fetching a customer's number using the universal search parameter
        """
        response = self.query_with_token(
            self.access_token, customer_universal_query.format(
                search_item=self.customer_2.primary_mobile_number))
        self.assertEqual(
            self.customer_2.first_name,
            response['data']['customer'][0]['firstName'])

    def test_query_customer_using_name(self):
        response = self.query_with_token(
            self.access_token,
            customer_name_query.format(name=self.customer_2.first_name))
        self.assertEqual(
            self.customer_2.last_name,
            response['data']['customer'][0]['lastName'])

    def test_query_customer_using_mobile_number(self):
        response = self.query_with_token(
            self.access_token, customer_number_query.format(
                mobile_number=self.customer_2.primary_mobile_number))
        self.assertEqual(
            self.customer_2.first_name,
            response['data']['customer'][0]['firstName'])

    def test_query_customer_using_id(self):
        customer_id = self.customer_2.id
        response = self.query_with_token(
            self.access_token, customer_id_query.format(
                customer_id=customer_id))
        self.assertEqual(
            self.customer_2.first_name,
            response['data']['customer'][0]['firstName'])

    def test_valid_filter_params(self):
        response = self.query_with_token(
            self.access_token, customer_search_query.format(
                search_key='firstName_Iexact',
                search_term=self.customer_2.first_name))
        self.assertEqual(
            self.customer_2.first_name,
            response['data']['filterCustomers']
            ['edges'][0]['node']['firstName'])
    
    def test_valid_filter_pagination_params(self):
        response = self.query_with_token(
            self.access_token,customer_filter_paginated)
        self.assertEqual(len(response["data"]['filterCustomers']['edges']), 1)
        self.assertEqual(response["data"]["totalCustomersPagesCount"],2)

    def test_invalid_email_params(self):
        email = 'Habib'
        response = self.query_with_token(
            self.access_token, customer_search_query.format(
                search_key='email_Iexact', search_term=email))
        expected_message = "['Please provide a valid email']"
        self.assertIn('errors', response)
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_invalid_search_params(self):
        first_name = 'H@bib'
        response = self.query_with_token(
            self.access_token, customer_search_query.format(
                search_key='firstName_Iexact', search_term=first_name))
        expected_message = (
            "['Please provide a valid search keyword."
            " Only letters, numbers, and apostrophes allowed']")
        self.assertIn('errors', response)
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_default_pagination_query(self):
        response = self.query_with_token(
            self.access_token, customer_query_paginated)
        self.assertEqual(response["data"]["totalCustomersPagesCount"], 1)

    def test_total_customer_query(self):
        response = self.query_with_token(
            self.access_token, customer_total_number_query)
        self.assertEqual(response['data']['totalCustomersCount'],0)
        

    def test_custom_pagination_query(self):
        CustomerFactory.create_batch(size=12)
        response = self.query_with_token(
            self.access_token,
            customer_custom_query_paginated.format(pageCount=5, pageNumber=1))
        self.assertEqual(response["data"]["totalCustomersPagesCount"], 3)
