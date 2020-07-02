from django.urls import reverse
from graphql_jwt.testcases import JSONWebTokenTestCase
from healthid.tests.authentication.test_data import loginUser_mutation
from healthid.tests.base_config import BaseConfiguration
from rest_framework.test import APIClient


class CsvExportTestCase(BaseConfiguration, JSONWebTokenTestCase):

    def setUp(self):
        super().setUp()
        # Log in user and use fetched token for endpoint authorization
        email = self.new_user["email"]
        password = self.new_user["password"]
        response = self.client.execute(loginUser_mutation.format(
            email=email,
            password=password)
        )
        token = response.data['loginUser']['restToken']
        self.auth_headers = {
            'HTTP_AUTHORIZATION':
            ' Token ' + str(token)
        }
        self.client = APIClient()
        self.url = reverse('export_csv', kwargs={'param': 'products'})

    def test_csv_export_including_specific_fields(self):
        body = {
            "product_name": True,
            "description": True
        }
        response = self.client.post(self.url, body,
                                    format='json', **self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_csv_export_excluding_specific_fields(self):
        body = {
            "product_name": False,
            "description": False
        }
        response = self.client.post(self.url, body,
                                    format='json', **self.auth_headers)
        self.assertEqual(response.status_code, 200)

    def test_csv_export_with_wrong_field_names(self):
        body = {
            "product": False,
            "description": False
        }
        response = self.client.post(self.url, body,
                                    format='json', **self.auth_headers)
        self.assertIn('error', response.data)
        self.assertEqual(response.status_code, 404)

    def test_empty_product_csv_export_succeeds(self):
        self.url = reverse('export_csv_file', kwargs={'param': 'products'})
        response = self.client.get(self.url,
                                   format='json', **self.auth_headers)
        content_type = response._headers['content-type'][1]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_type, 'text/csv')

    def test_empty_batch_info_csv_export(self):
        self.url = reverse('export_csv_file', kwargs={'param': 'batch_info'})
        response = self.client.get(
            self.url, cformat='json', **self.auth_headers)
        content_type = response._headers['content-type'][1]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_type, 'text/csv')
