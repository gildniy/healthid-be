from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.authentication import (
    create_role,
    get_role_by_id,
    get_role_by_name,
    edit_role,
    get_roles,
    create_role_with_empty_name)
from healthid.utils.messages.authentication_responses import (
    AUTH_ERROR_RESPONSES)


class GraphQLTestCase(BaseConfiguration):
    """
    Testing the role functions
    """

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        self.assertNotIn("errors", resp, "Response had errors")
        self.assertEqual(resp["data"], expected, "Response has correct data")

    def test_create_role(self):
        data = {
            "name": "User"
        }
        expected = {"createRole": {"success": True, "role": {"name": "User"}}}
        resp = self.query_with_token(
            self.access_token_master, create_role.format(
                **data))
        self.assertResponseNoErrors(resp, expected)

    def test_create_role_with_empty_name(self):

        expected_message = AUTH_ERROR_RESPONSES["empty_role_name"]
        resp = self.query_with_token(
            self.access_token_master, create_role_with_empty_name)
        self.assertEqual(resp['errors'][0]['message'], expected_message)

    def test_single_role_by_id(self):
        role = {
            "id": self.role.id
        }
        resp = self.query_with_token(
            self.access_token_master, get_role_by_id.format(
                **role
            ))
        self.assertResponseNoErrors(
            resp, {"role": {"id": str(self.role.id),
                            "name": str(self.role.name)}}
        )

    def test_single_role_by_name(self):
        role = {
            "name": self.role.name
        }
        response = self.query_with_token(
            self.access_token_master, get_role_by_name.format(
                **role))
        self.assertNotIn('errors', response)
        self.assertEqual(self.role.name, response['data']['role']['name'])

    def test_all_roles(self):
        response = self.query_with_token(
            self.access_token_master, get_roles)
        self.assertNotIn('errors', response)
        self.assertIn('data', response)

    def test_edit_role(self):
        role = {
            "id": self.role.id
        }
        expected = {"editRole": {"success": True,
                                 "role": {"name": "Test Role"}}}
        resp = self.query_with_token(
            self.access_token_master, edit_role.format(
                **role
            ))
        self.assertResponseNoErrors(resp, expected)

    def test_delete_role(self):
        query_string = f"""
           mutation deleteRole {{
           deleteRole (id:"{self.role.id}") {{
            success
          }}
        }}
        """
        expected = {"deleteRole": {"success": True}}
        resp = self.query_with_token(
            self.access_token_master, query_string)
        self.assertResponseNoErrors(resp, expected)
