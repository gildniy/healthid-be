from django.conf import settings
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.authentication import (
    register_user_query, user)
from healthid.utils.messages.authentication_responses import\
    AUTH_ERROR_RESPONSES, AUTH_SUCCESS_RESPONSES


FRONTEND_URL = settings.FRONTEND_URL
HTTP = settings.HTTP


class VerificationTestCase(BaseConfiguration):

    def addUser(self):
        response = self.query(
            register_user_query.format(**user)
        )
        return response

    def test_account_verified(self):
        response = self.addUser()
        verification_link = response['data']['createUser']['verificationLink']
        response = self.client.get(
            verification_link,
            content_type='application/json')
        self.assertIn(
            f'{settings.HTTP}://{settings.FRONTEND_URL}',
            response.context[0]['link'])
        self.assertEqual(200, response.status_code)

    def test_account_already_verified_user(self):
        response = self.addUser()
        verification_link = response['data']['createUser']['verificationLink']
        self.client.get(verification_link, content_type='application/json')
        response = self.client.get(
            verification_link,
            content_type='application/json')
        self.assertIn(
            (AUTH_SUCCESS_RESPONSES["account_verification"]),
            response.context[0]['small_text_detail'])
        self.assertEqual(409, response.status_code)

    def test_expired_token(self):
        response = self.addUser()
        verification_link = response['data']['createUser']['verificationLink']
        response = self.client.get(
            verification_link+'23',
            content_type='application/json')
        self.assertIn((AUTH_ERROR_RESPONSES["account_verification_fail"]),
                      response.context[0]['small_text_detail'])
        self.assertEqual(401, response.status_code)

    def test_corrupted_token(self):
        self.addUser()
        ubd6 = 'MjQ5OHlva3V3'
        token = '56c-b773cdcdd485651e945e'
        response = self.client.get(
            f'http://{settings.FRONTEND_URL}/healthid/activate/{ubd6}/{token}',
            content_type='application/json')
        self.assertIn(AUTH_ERROR_RESPONSES["verification_link_corrupt"],
                      response.context[0]['small_text_detail'])
        self.assertEqual(401, response.status_code)
