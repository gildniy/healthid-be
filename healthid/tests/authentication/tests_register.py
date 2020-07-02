import json

from django.core import mail
from django.test import Client, TestCase

from healthid.apps.authentication.models import Role
from healthid.tests.authentication.test_data import register_user_query


class TestRegisterMutation(TestCase):
    """handles user registration tests"""

    def setUp(self):
        self._client = Client()

        self.user_data = {
            'password': 'Password12',
            'email': 'healthid@gmail.com',
            'mobileNumber': "+256 788088831"
        }

    def query(self, query: str):
        body = {'query': query}
        response = self._client.post(
            '/healthid/',
            json.dumps(body),
            content_type='application/json',
        )
        json_response = json.loads(response.content.decode())
        return json_response

    def create_default_role(self, role_name):
        return Role.objects.create(name=role_name)

    def test_create_user(self):
        """method for creating a user"""
        response = self.query(register_user_query.format(**self.user_data), )
        self.assertNotIn('errors', response)
        self.assertIn('success', response['data']['createUser'])

    def test_create_wrong_password(self):
        """tests for a weak password"""
        self.user_data['password'] = 'weakpassword'
        response = self.query(register_user_query.format(**self.user_data), )
        self.assertIn('errors', response)
        self.assertNotIn('success', response)

    def test_create_wrong_mobileNumber(self):
        """tests invalid mobile number"""
        self.user_data['mobileNumber'] = '2345'
        response = self.query(register_user_query.format(**self.user_data), )
        self.assertIn('errors', response)
        self.assertNotIn('success', response)

    def test_create_wrong_email(self):
        """tests invalid email adress"""
        self.user_data['email'] = 'usergmail.com'
        response = self.query(register_user_query.format(**self.user_data), )
        self.assertIn('errors', response)
        self.assertNotIn('success', response)

    def test_register_mutation_user_error(self):
        """user with the same email already exists"""
        response = self.query(register_user_query.format(**self.user_data), )
        response = self.query(register_user_query.format(**self.user_data), )
        self.assertIn('errors', response['data']['createUser'])

    def test_mail_sent_successfully(self):
        """Tests whether the confirmation email was sent successfully"""
        self.create_default_role(role_name="Master Admin")
        response = self.query(register_user_query.format(**self.user_data), )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('success', response['data']['createUser'])
