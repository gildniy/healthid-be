from healthid.tests.base_config import BaseConfiguration
from healthid.tests.authentication.test_data import query_str
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.authentication_responses import\
     AUTH_ERROR_RESPONSES


class TestAdminRegistration(BaseConfiguration):

    def test_update_admin_profile(self):

        response = self.query_with_token(
            self.access_token_master,
            query_str.format(**self.update_user_data))
        self.assertNotIn('errors', response)
        self.assertIn('success',
                      response['data']['updateAdminUser']
                      )

    def test_update_admin_profile_doesnot_exists(self):
        self.user.delete()
        response = self.query_with_token(
            self.access_token,
            query_str.format(**self.update_user_data))
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            ERROR_RESPONSES["authorization_error"]
        )

    def test_update_admin_profile_with_invalid_email(self):
        self.update_user_data['id'] = str(self.user.id)
        self.update_user_data['email'] = 'invalidemailadress'
        response = self.query_with_token(
            self.access_token_master,
            query_str.format(**self.update_user_data))
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            'invalidemailadress is not a valid email address'
        )

    def test_update_admin_profile_with_invalid_username(self):
        self.update_user_data['id'] = str(self.user.id)
        self.update_user_data['username'] = '#$**********'
        response = self.query_with_token(
            self.access_token_master,
            query_str.format(**self.update_user_data))
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            AUTH_ERROR_RESPONSES["special_characters_error"].format("names")
        )

    def test_update_admin_profile_with_invalid_phone_number(self):
        self.update_user_data['id'] = str(self.user.id)
        self.update_user_data['mobile_number'] = '00778'
        response = self.query_with_token(
            self.access_token_master,
            query_str.format(**self.update_user_data))
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            ERROR_RESPONSES["invalid_field_error"].format(
                "mobile number (ex. +2346787646)")
        )

    def test_update_admin_profile_with_very_long_name(self):
        self.update_user_data['id'] = str(self.user.id)
        self.update_user_data['lastname'] = 'verylongne'*100
        response = self.query_with_token(
            self.access_token_master,
            query_str.format(**self.update_user_data))
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            AUTH_ERROR_RESPONSES["characters_exceed_error"].format("a name")
        )

    def test_update_admin_profile_with_empty_name_field(self):
        self.update_user_data['id'] = str(self.user.id)
        self.update_user_data['lastname'] = ''
        response = self.query_with_token(
            self.access_token_master,
            query_str.format(**self.update_user_data))
        self.assertIn('errors', response)
        self.assertEqual(
            response['errors'][0]['message'],
            ERROR_RESPONSES["empty_field_error"].format("name field")
        )
