from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.authentication import \
    update_user_role_query, add_user_business_query


class TestUserRole(BaseConfiguration):
    """
    Testing Adding user by the Master Admin
    """

    def test_add_user(self):
        """
        test user creation
        """
        user_data = {
            'userId': self.user.id,
            'roleId': self.role.id
        }
        resp = self.query_with_token(
            self.access_token_master,
            update_user_role_query.format(**user_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['updateRole']['errors'], None)
        self.assertEqual(resp['data']['updateRole']
                         ['user']['email'], self.user.email)
        self.assertEqual(resp['data']['updateRole']
                         ['user']['role']['name'], self.role.name)

    def test_add_user_business(self):
        """
        test user creation
        """
        user_data = {
            'userId': self.user.id,
            'businessId': self.business.id
        }
        resp = self.query_with_token(
            self.access_token_master,
            add_user_business_query.format(**user_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['addUserBusiness']['errors'], None)
        self.assertEqual(resp['data']['addUserBusiness']
                         ['user']['email'], self.user.email)
