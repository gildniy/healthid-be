import os
from django.core.management import call_command
from django.test import RequestFactory
from django.urls import reverse
from graphql_jwt.testcases import JSONWebTokenTestCase
from healthid.apps.orders.models import PaymentTerms, Suppliers, Tier
from healthid.tests.authentication.test_data import loginUser_mutation
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.suppliers import (
    supplier_mutation, suppliers_query, suppliers_totalnumber_query,
    supplier_query_by_id, supplier_query_by_name, email_invalid,
    mobile_invalid
)
from healthid.views import HandleCSV
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from rest_framework.test import APIClient
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES
from healthid.tests.factories import SuppliersFactory


class SuppliersTestCase(BaseConfiguration, JSONWebTokenTestCase):
    def setUp(self):
        super(SuppliersTestCase, self).setUp()
        self.factory = RequestFactory()
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        login_admin = self.client.execute(loginUser_mutation.format(
            **self.login_master_admin
        ))

        login_admin_another_business = self.client.execute(loginUser_mutation.format(
            **self.login_third_master_admin
        ))

        master_admin_rest_token = login_admin.data['loginUser']['restToken']
        self.admin_auth_headers = {
            'HTTP_AUTHORIZATION':
            ' Token ' + str(master_admin_rest_token)
        }

        master_admin2_rest_token = login_admin_another_business.data['loginUser']['restToken']
        self.admin2_auth_headers = {
            'HTTP_AUTHORIZATION':
            ' Token ' + str(master_admin2_rest_token)
        }

        call_command('loaddata', 'healthid/fixtures/tests')
        self.view = HandleCSV.as_view()
        self.client = APIClient()
        self.url = reverse('export_csv', kwargs={'param': 'products'})

        self.supplier_1 = SuppliersFactory()

        self.supplier_data = {
            "id": self.supplier_1.id,
            "name": self.supplier_1.name
        }

    def handle_csv_request(self, path):
        file = open(path, 'rb')
        request = self.factory.post(
            reverse('handle_csv', args=['suppliers']), {'file': file},
            **self.admin_auth_headers)
        self.view
        return request

    def handle_csv_request_different_business(self, path):
        file = open(path, 'rb')
        request = self.factory.post(
            reverse('handle_csv', args=['suppliers']), {'file': file},
            **self.admin2_auth_headers)
        self.view
        return request

    def test_models(self):
        supplier = Suppliers()
        supplier.name = "Ntale"
        tier = Tier()
        tier.name = 'manufacturer'
        payment_term = PaymentTerms()
        payment_term.name = 'on credit'
        assert (str(supplier) == 'Ntale')
        assert (str(tier) == 'manufacturer')
        assert (str(payment_term) == 'on credit')

    def test_suppliers_query(self):
        response = self.query_with_token(self.access_token_master,
                                         suppliers_query)
        self.assertIn('data', response)
        self.assertNotIn('errors', response)

    def test_suppliers_totalnumber_query(self):
        response = self.query_with_token(
            self.access_token_master, suppliers_totalnumber_query)
        self.assertIn('data', response)
        self.assertNotIn('errors', response)
        self.assertEqual(1, response["data"]["totalNumberOfSuppliers"])

    def test_supplier_query_by_id(self):
        response = self.query_with_token(self.access_token_master,
                                         supplier_query_by_id.format(
                                             **self.supplier_data))
        supplier_id = self.supplier_data['id']

        self.assertNotIn('errors', response)
        self.assertEqual(supplier_id, response['data']['singleSupplier']['id'])

    def test_supplier_query_by_name(self):
        response = self.query_with_token(self.access_token_master,
                                         supplier_query_by_name.format(
                                             **self.supplier_data))
        supplier_name = self.supplier_data['name']

        self.assertNotIn('errors', response)
        self.assertEqual(
            supplier_name, response['data']['singleSupplier']['name'])

    def test_supplier_query_with_empty_field(self):
        data = {
            "name": ""
        }
        response = self.query_with_token(self.access_token_master,
                                         supplier_query_by_name.format(
                                             **data))
        message = ORDERS_ERROR_RESPONSES[
            "invalid_supplier_field"]
        self.assertEqual(
            message,
            response['errors'][0]['message'])

    def test_create_supplier(self):
        response = self.query_with_token(
            self.access_token_master, supplier_mutation)
        self.assertIn('data', response)
        self.assertNotIn('errors', response)

    def test_create_supplier_to_another_business(self):
        response = self.query_with_token(
            self.login_third_master_admin_token, supplier_mutation)
        self.assertIn('data', response)
        self.assertNotIn('errors', response)

    def test_invalid_email_supplier(self):
        response = self.query_with_token(
            self.access_token_master, email_invalid)
        message = ORDERS_ERROR_RESPONSES["invalid_email"]
        self.assertEqual(
            message,
            response['errors'][0]['message'])

    def test_invalid_mobile_supplier(self):
        response = self.query_with_token(
            self.access_token_master, mobile_invalid)
        msg_format = "mobile number (ex. +2346787646)"
        message = ERROR_RESPONSES['invalid_field_error'].format(msg_format)
        self.assertEqual(
            message,
            response['errors'][0]['message'])

    def test_csv_file_upload(self):
        path = os.path.join(self.base_path, 'test.csv')
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 201)
        self.assertIn('success', response.data)
        # test dupplication
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 400)
        self.assertIn('duplicatedSuppliers', response.data)

    def test_invalid_csv_data(self):
        path = os.path.join(self.base_path, 'invalid_csv.csv')
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 400)
        self.assertIn('rows', response.data)
        self.assertIn('columns', response.data)
        self.assertEqual(response.data.get('rows')[0].get('1')['email'],
                         ERROR_RESPONSES['required_field'].format('email'))
        self.assertEqual(response.data.get('columns')[0],
                         ERROR_RESPONSES['not_allowed_field']
                         .format('nameeee'))

    def test_invalid_csv_with_missing_column(self):
        path = os.path.join(self.base_path, 'missing_column.csv')
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 400)
        self.assertIn(ERROR_RESPONSES["csv_missing_field"],
                      str(response.data['error']))

    def test_invalid_csv_with_more_column(self):
        path = os.path.join(self.base_path, 'more_column.csv')
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 400)
        self.assertIn(ERROR_RESPONSES["csv_many_field"],
                      str(response.data['error']))

    def test_invalid_on_credit(self):
        path = os.path.join(self.base_path, 'invalid_on_credit.csv')
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 400)
        self.assertIn(ERROR_RESPONSES["payment_terms_on_credit"].format(1),
                      str(response.data['error']))

    def test_invalid_cash_on_delivery(self):
        path = os.path.join(self.base_path, 'invalid_cash_on_delivery.csv')
        request = self.handle_csv_request(path)
        response = self.view(request, param='suppliers')
        self.assertEqual(response.status_code, 400)
        self.assertIn(ERROR_RESPONSES["payment_terms_cash_on_deliver"].
                      format(1), str(response.data['error']))

    def test_empty_suppliers_csv_export_succeeds(self):
        self.url = reverse('export_csv_file', kwargs={'param': 'suppliers'})
        response = self.client.get(self.url,
                                   format='json', **self.admin_auth_headers)
        content_type = response._headers['content-type'][1]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_type, 'text/csv')

    def test_empty_suppliers_csv_export_failure(self):
        self.url = reverse('export_csv_file', kwargs={'param': 'supplier'})
        response = self.client.get(self.url,
                                   format='json', **self.admin_auth_headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, ERROR_RESPONSES['wrong_param'])

    def test_retail_pro_suppliers(self):
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'retail_pro_suppliers.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['suppliers']), {'file': file},
            **self.admin_auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='retail_pro_suppliers')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["success"],
                         "Successfully added supplier(s)")
        self.assertEqual(response.data["noOfSuppliersAdded"], 1)
        self.assertEqual(response.data["duplicatedSuppliers"], [])

    def test_quick_books_csv_suppliers_upload(self):
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'quick_books_suppliers.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['suppliers']), {'file': file},
            **self.admin_auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='quick_books_suppliers')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["success"],
                         "Successfully added supplier(s)")
        self.assertEqual(response.data["noOfSuppliersAdded"], 1)
        self.assertEqual(response.data["duplicatedSuppliers"], [])
