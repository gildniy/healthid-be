from healthid.apps.register.models import Register
from healthid.tests.register.base import RegisterBaseCase
from healthid.tests.test_fixtures.register import (create_register_query,
                                                   delete_register_query,
                                                   query_register,
                                                   update_register_query,
                                                   registers_query)
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class RegisterTestCase(RegisterBaseCase):

    def test_empty_db(self):
        resp = self.query_with_token(self.access_token_master,
                                     '{register{id}}')
        self.assertIn('errors', resp)

    def test_single_register(self):
        register = self.create_register()
        resp = self.query_with_token(
            self.access_token_master, query_register(register.id))
        self.assertResponseNoErrors(
            resp, {"register": {"id": str(register.id)}})
        self.assertIn('data', resp)

    def test_create_register(self):
        outlet = self.outlet
        response = self.query_with_token(
            self.access_token_master,
            create_register_query(outlet.id, 3),)
        self.assertEqual(
            3, len(response["data"]["createRegister"]["registers"]))
        self.assertEqual("liver moore 1",
                         response["data"]["createRegister"]["registers"][0]["name"])

    def test_update_register(self):
        register = self.create_register()
        data = {
            "register_id": register.id
        }
        response = self.query_with_token(
            self.access_token_master,
            update_register_query.format(**data))
        message = SUCCESS_RESPONSES["update_success"].format(
            "Register")
        self.assertResponseNoErrors(
            response,
            {
                "updateRegister": {
                    'message': message,
                    'register': {'name': 'ever moore'},
                    "success": True
                }
            }
        )

    def test_query_register(self):
        response = self.query_with_token(
            self.access_token_master, registers_query)
        self.assertIn("data", response)

    def test_delete_register(self):
        register = self.create_register()
        response = self.query_with_token(
            self.access_token_master, delete_register_query(register.id),)
        self.assertIn("success", response["data"]["deleteRegister"])

    def test_delete_invalid_register(self):
        response = self.query_with_token(
            self.access_token_master, delete_register_query(40),)
        self.assertIn("errors", response)

    def test_register_model(self):
        register = self.create_register()
        registers = Register.objects.all()
        self.assertQuerysetEqual(registers,
                                 [f'<Register: {register.name}>'])
