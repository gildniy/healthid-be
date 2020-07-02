import os
from rest_framework import status
from django.core.management import call_command
from django.test import RequestFactory
from django.urls import reverse
from graphql_jwt.testcases import JSONWebTokenTestCase
from healthid.tests.authentication.test_data import loginUser_mutation
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.products import supplier_mutation
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES
from healthid.utils.messages.products_responses import (
    PRODUCTS_SUCCESS_RESPONSES
)
from healthid.views import HandleCSV


class TestCsvUpload(BaseConfiguration, JSONWebTokenTestCase):
    def setUp(self):
        super(TestCsvUpload, self).setUp()
        # Log in user and use fetched token for endpoint authorization
        email = self.new_user["email"]
        password = self.new_user["password"]
        response = self.client.execute(loginUser_mutation.format(
            email=email,
            password=password)
        )
        token = response.data['loginUser']['restToken']

        self.query_with_token(self.access_token_master,
                              supplier_mutation)
        self.auth_headers = {
            'HTTP_AUTHORIZATION':
            ' Token ' + str(token)
        }
        call_command('loaddata', 'healthid/fixtures/product_csv')
        call_command('loaddata', 'healthid/fixtures/orders_products')

    def test_csv_file_upload_products(self):
        self.business.user = self.user
        self.business.save()
        self.product_category.business = self.business
        self.product_category.save()
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'product.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['products']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='products')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('noOfProductsAdded', response.data)
        self.assertGreater(response.data['noOfProductsAdded'], 0)

    def test_retail_pro_csv_file_upload_products(self):
        self.business.user = self.user
        self.business.save()
        self.product_category.business = self.business
        self.product_category.save()
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'retail_pro_product.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['products']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='retail_pro_products')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('noOfProductsAdded', response.data)
        self.assertIn('noOfProductsUpdated', response.data)
        self.assertIn('noOfErrorsEncountered', response.data)
        self.assertEqual(response.data.get('noOfProductsAdded'),1)        
        self.assertEqual(response.data.get('noOfProductsUpdated'),0)
        self.assertEqual(response.data.get('noOfErrorsEncountered'),0)

    def test_quick_books_csv_file_upload_products(self):
        self.business.user = self.user
        self.business.save()
        self.product_category.business = self.business
        self.product_category.save()
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'quickbooks_products.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['products']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='quick_books_products')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('noOfProductsAdded', response.data)
        self.assertIn('noOfProductsUpdated', response.data)
        self.assertIn('noOfErrorsEncountered', response.data)
        self.assertEqual(response.data.get('noOfProductsAdded'), 1)
        self.assertEqual(response.data.get('noOfProductsUpdated'), 0)
        self.assertEqual(response.data.get('noOfErrorsEncountered'), 0)

    def test_invalid_csv_file_upload_products(self):
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base_path, 'invalid_product.csv')
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['products']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='products')
        self.assertEqual(response.status_code, 400)
        self.assertIn('rows', response.data)
        self.assertIn('columns', response.data)
        self.assertEqual(response.data.get('rows')[0].get('1')['name'],
                         ERROR_RESPONSES['required_field'].format('name'))
        self.assertEqual(response.data.get('columns')[0],
                         ERROR_RESPONSES['not_allowed_field']
                         .format('not allowed column'))

    def test_successful_batch_upload(self):
        self.business.user = self.user
        self.business.save()
        self.product.business = self.business
        self.product.save()
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(
            base_path,
            'batch_info_csv_samples/valid_batch_info.csv'
        )
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['batch_info']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='batch_info')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data['success'],
            PRODUCTS_SUCCESS_RESPONSES["batch_upload_success"]
        )

    def test_invalid_batch_column_header_upload(self):
        self.business.user = self.user
        self.business.save()
        self.product.business = self.business
        self.product.save()
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(
            base_path,
            'batch_info_csv_samples/invalid_header.csv'
        )
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['batch_info']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='batch_info')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data[0],
                         PRODUCTS_ERROR_RESPONSES["batch_csv_error"]
                         )

    def test_invalid_batch_boolean(self):
        self.business.user = self.user
        self.business.save()
        self.product.business = self.business
        self.product.save()
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(
            base_path,
            'batch_info_csv_samples/invalid_boolean.csv'
        )
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['batch_info']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='batch_info')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data[0],
                         PRODUCTS_ERROR_RESPONSES["batch_bool_error"]
                         )

    def test_invalid_batch_expiry_date(self):
        self.business.user = self.user
        self.business.save()
        self.product.business = self.business
        self.product.save()
        factory = RequestFactory()
        base_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(
            base_path,
            'batch_info_csv_samples/invalid_expiry_date.csv'
        )
        file = open(path, 'rb')
        request = factory.post(
            reverse('handle_csv', args=['batch_info']), {'file': file},
            **self.auth_headers)
        view = HandleCSV.as_view()
        response = view(request, param='batch_info')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data[0],
                         PRODUCTS_ERROR_RESPONSES["batch_expiry_error"].format
                         ('Pizza')
                         )
