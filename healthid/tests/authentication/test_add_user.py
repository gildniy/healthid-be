from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.authentication import \
    add_user_query, admin_update_user_query
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES
from healthid.utils.messages.authentication_responses import\
     AUTH_ERROR_RESPONSES


class TestAddUser(BaseConfiguration):
    """
    Testing Adding user by the Master Admin
    """

    def test_add_user(self):
        """
        test user creation
        """
        email = 'test@gmail.com'
        mobile_number = '+256754434487'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': self.role.id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['addUser']['errors'], None)
        self.assertEqual(resp['data']['addUser']
                         ['user']['email'], email)
        self.assertEqual(resp['data']['addUser']
                         ['user']['mobileNumber'], mobile_number)

    def test_update_user(self):
        email = 'newemail@test.com'
        firstname = 'newfirstname'
        job_title = 'Supervisor'
        mobile_number = '+256754434483'
        user_id = self.user.id
        user_data = {
            'firstname': firstname,
            'jobTitle': job_title,
            'mobileNumber': mobile_number,
            'email': email,
            'id': user_id
        }
        resp = self.query_with_token(
            self.access_token_master,
            admin_update_user_query.format(**user_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['adminUpdateUser']['errors'], None)
        self.assertEqual(resp['data']['adminUpdateUser']
                         ['user']['email'], email)
        self.assertEqual(resp['data']['adminUpdateUser']
                         ['user']['mobileNumber'], mobile_number)
        self.assertEqual(resp['data']['adminUpdateUser']
                         ['user']['jobTitle'], job_title)

    def test_wrong_email(self):
        """
        test wrong email
        """
        email = 'test@gmail'
        mobile_number = '+256754434487'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': self.role.id
        }

        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn(ERROR_RESPONSES["invalid_field_error"].format("email"),
                      resp['errors'][0]['message'])

    def test_wrong_mobile_number(self):
        """
        test wrong mobile_number
        """
        email = 'test@gmail.com'
        mobile_number = '+256754'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': self.role.id

        }
        example = "mobile number (ex. +2346787646)"
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn(ERROR_RESPONSES["invalid_field_error"].format(example),
                      resp['errors'][0]['message'])

    def test_existing_email(self):
        # test if the email already exists
        email = 'john.doe@gmail.com'
        mobile_number = '+256754434487'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': self.role.id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertEqual(resp['data']['addUser']
                         ['errors'], ['Something went wrong: User with email '
                                      'john.doe@gmail.com already exists'])

    def test_empty_outlet_id(self):
        """
        test user creation
        """
        email = 'test@gmail.com'
        mobile_number = '+256754434487'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': '',
            'roleId': self.role.id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn('errors', resp)
        self.assertIn(ERROR_RESPONSES["empty_field_error"].format("Outlet Id"),
                      resp['errors'][0]['message'])

    def test_invalid_outlet_id(self):
        """
        test user creation
        """
        email = 'test@gmail.com'
        mobile_number = '+256754434487'
        outlet_id = '12121212'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': outlet_id,
            'roleId': self.role.id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn('errors', resp)
        self.assertIn(OUTLET_ERROR_RESPONSES[
                      "inexistent_outlet"].format(outlet_id),
                      resp['errors'][0]['message'])

    def test_invalid_role_id(self):
        """
        test user creation
        """
        email = 'test@gmail.com'
        mobile_number = '+256754434487'
        role_id = '12121212'
        user_data = {
            'email': email,
            'mobileNumber': mobile_number,
            'outletId': self.outlet.id,
            'roleId': role_id

        }
        resp = self.query_with_token(
            self.access_token_master, add_user_query.format(**user_data))
        self.assertIn('errors', resp)
        self.assertIn(AUTH_ERROR_RESPONSES["inexistent_role"].format(role_id),
                      resp['errors'][0]['message'])
