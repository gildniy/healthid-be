from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.create_d_queue import\
    (create_email_despatch)
from healthid.apps.authentication.models import User


class TestDespatchQueue(BaseConfiguration):
    """
    Testing Adding user by the Master Admin
    """

    def test_create_despatch(self):
        """
        test user creation
        """
        new_user = {
            "email": "john34.doe@gmail.com",
            "mobile_number": "+2567707788",
            "password": "Password123"
        }
        user = User.objects.create_user(**new_user)
        user.active = True
        despatch_date = {
            'recipient_ids': user.id,
        }
        resp = self.query_with_token(
            self.access_token_master,
            create_email_despatch.format(**despatch_date))
        self.assertEqual(
            resp['data']['createEmailNotifications']
            ['queues'][0]['status'], 'SENT')

    def test_create_despatch_id_exist(self):
        """
        test user id exist
        """
        despatch_date = {
            'recipient_ids': [self.user.id],
        }
        resp = self.query_with_token(
            self.access_token_master,
            create_email_despatch.format(**despatch_date))
        self.assertIn('errors', resp)
