from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.login import login_user, login_user_email
from healthid.utils.messages.authentication_responses import\
     AUTH_ERROR_RESPONSES, AUTH_SUCCESS_RESPONSES


class LoginTestCase(BaseConfiguration):

    def test_login_user(self):
        response = self.query(
            login_user(
                self.new_user['mobile_number'], self.new_user['password'])
        )
        self.assertIn(AUTH_SUCCESS_RESPONSES["login_success"],
                      response["data"]["loginUser"]['message'])

    def test_login_email(self):
        response = self.query(
            login_user_email(
                self.new_user['email'], self.new_user['password'])
        )
        self.assertIn(AUTH_SUCCESS_RESPONSES["login_success"],
                      response["data"]["loginUser"]['message'])

    def test_invalid_login(self):
        response = self.query(
            login_user_email("me@you", "this"))
        self.assertIn(AUTH_ERROR_RESPONSES["login_validation_error"],
                      response["errors"][0]['message'])

    def test_invalid_number(self):
        response = self.query(
            login_user("25499999999", "this"))
        self.assertIn(AUTH_ERROR_RESPONSES["login_validation_error"],
                      response["errors"][0]['message'])
