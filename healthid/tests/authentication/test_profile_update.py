from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.authentication import (update_email_query,
                                                         update_image_query,
                                                         update_username_query)
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.authentication_responses import\
     AUTH_ERROR_RESPONSES


class TestProfileUpdate(BaseConfiguration):
    """
    Class to test for updates to the following user details:
    1. username
    2. profile image
    3. primary email
    """

    def test_username_update(self):
        # test if the username can be updated.
        username = "newUsername"
        response = self.query_with_token(
            self.access_token, update_username_query.format(username))

        self.assertIn('data', response)
        self.assertEqual(response['data']['updateUser']['error'], None)
        self.assertEqual(response['data']['updateUser']
                         ['user']['username'], username)

    def test_email_update(self):
        # test if user email can be updated
        email = "jillo.woche@andela.com"
        response = self.query_with_token(
            self.access_token, update_email_query.format(email))

        self.assertIn('data', response)
        self.assertEqual(response['data']['updateUser']['error'], None)
        self.assertEqual(response['data']['updateUser']
                         ['user']['email'], email)

    def test_image_update(self):
        # test if user image can be updated
        profile_image = "https://d1nhio0ox7pgb.cloudfront.net/plain/user.png"
        response = self.query_with_token(
            self.access_token, update_image_query.format(profile_image))

        self.assertIn('data', response)
        self.assertEqual(response['data']['updateUser']['error'], None)
        self.assertEqual(response['data']['updateUser']
                         ['user']['profileImage'], profile_image)

    # testing for invalid inputs
    def test_empty_username(self):
        # test if update can be made with an empty username field
        username = ""
        response = self.query_with_token(
            self.access_token, update_username_query.format(username))

        self.assertIn("contain special characters",
                      response['errors'][0]['message'])

    def test_special_characters_username(self):
        # test for update with usernames with special characters
        username = "$dollarSign$"
        response = self.query_with_token(
            self.access_token, update_username_query.format(username))
        self.assertIn("contain special characters",
                      response['errors'][0]['message'])

    def test_invalid_email(self):
        # test if update can be made with an empty email field
        email = ""
        response = self.query_with_token(
            self.access_token, update_email_query.format(email))
        self.assertIn(ERROR_RESPONSES["invalid_field_error"].format("email"),
                      response['errors'][0]['message'])

    def test_existing_email(self):
        # test if a user can update to an already
        # existing email
        email = "john.doe@gmail.com"
        response = self.query_with_token(
            self.access_token, update_email_query.format(email))
        self.assertIn(AUTH_ERROR_RESPONSES["email_duplicate_error"],
                      response['errors'][0]['message'])
