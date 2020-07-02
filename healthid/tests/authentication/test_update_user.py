import json

from django.test import Client, TestCase

from healthid.apps.authentication.models import User


class UserUpdateTestCase(TestCase):
    def setUp(self):
        self._client = Client()
        self.user = User.objects.create_user(
            email="shadik.ntale@andela.com",
            password="Echo-pwned-01",
            mobile_number="+256770777777")
        self.user.is_active = True
        self.user.save()
        self._client.login(
            email="shadik.ntale@andela.com", password="Echo-pwned-01")

    def query(self, query: str = None):
        body = dict()
        body['query'] = query
        response = self._client.post(
            '/healthid/', json.dumps(body), content_type='application/json')
        json_response = json.loads(response.content.decode())
        return json_response

    def mutation_string_generator(self, **kwargs):
        new_password = kwargs.get('new_password')
        old_password = kwargs.get('old_password')
        mutation_string = '''
                    mutation{{
                            updateUser(
                                mobileNumber: "+256756565137"
                                password: [
                                {{
                                    oldPassword: "{oldPassword}",
                                    newPassword: "{newPassword}"
                                }}
                                ]
                            ),{{
                                error
                                success
                                user{{
                                email
                                mobileNumber
                                }}
                            }}
                            }}
                '''.format(
            newPassword=new_password, oldPassword=old_password)
        return mutation_string

    def test_get_all_users(self):
        response = self.query('query{ users {id} }')
        self.assertNotIn('errors', response)
        self.assertIn('data', response)

    def test_update_user(self):
        new_password = "Password123"
        old_password = "Echo-pwned-01"
        mutation_string = self.mutation_string_generator(
            new_password=new_password, old_password=old_password)

        response = self.query(mutation_string)
        self.assertIn('data', response)
        self.assertIsNotNone(response['data']['updateUser']['success'])
        self.assertIsNone(response['data']['updateUser']['error'])

    def test_cannot_update_with_unmatching_passwords(self):
        new_password = "Password1"
        old_password = "Password2"
        mutation_string = self.mutation_string_generator(
            new_password=new_password, old_password=old_password)

        response = self.query(mutation_string)
        self.assertIsNotNone(response['errors'][0]['message'])
        self.assertIsNone(response['data']['updateUser'])
