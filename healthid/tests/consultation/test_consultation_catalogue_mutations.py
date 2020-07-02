from faker import Faker

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.consultation import (
    create_consultation_item, edit_consultation_item,
    delete_consultation_item)
from healthid.utils.messages.common_responses import (
    SUCCESS_RESPONSES)
from healthid.tests.factories import (
    ConsultationItemFactory, CustomerFactory, CustomerConsultationFactory)


fake = Faker()


class TestConsultationCatalogue(BaseConfiguration):
    """
    Tests creating, updating and deleting a consultation item
    """

    def setUp(self):
        super(TestConsultationCatalogue, self).setUp()
        self.consultation_item = ConsultationItemFactory()
        self.customer_2 = CustomerFactory()
        self.customer_consultation = CustomerConsultationFactory(
            customer=self.customer_2)

        self.consultation_data = {
            "consultation_name": fake.word(),
            "description": fake.text(max_nb_chars=50),
            "consultant_role": "Pharmacist",
            "approved_formats": "Telephonic",
            "business_id": self.business.id,
            "minutes_per_session": fake.random_int(min=1, max=60),
            "price_per_session": fake.random_int()
        }

    def test_create_consultation_item(self):
        response = self.query_with_token(
            self.access_token_master, create_consultation_item.format(
                **self.consultation_data))

        success =\
            [SUCCESS_RESPONSES[
                'creation_success'].format(
                    self.consultation_data['consultation_name'])]

        self.assertNotIn('errors', response)
        self.assertEqual(
            str(success), response['data']['createConsultationItem']
            ['success'])
        self.assertEqual(
            self.consultation_data['consultation_name'], response['data']
            ['createConsultationItem']['consultation']['consultationName'])

    def test_create_already_existent_item(self):
        self.query_with_token(
            self.access_token_master, create_consultation_item.format(
                **self.consultation_data))
        response = self.query_with_token(
            self.access_token_master, create_consultation_item.format(
                **self.consultation_data))

        self.assertIn('errors', response)
        self.assertEqual(
            'ConsultationCatalogue with consultation_name {}, already exists!'.format(  # noqa
                self.consultation_data['consultation_name']),
            response['errors'][0]['message'])

    def test_edit_consultation_item(self):
        consultation_id = self.consultation_item.id

        update_data = {
            "consultation_id": consultation_id,
            "description": fake.text(max_nb_chars=50)
        }

        message =\
            [SUCCESS_RESPONSES[
                'update_success'].format('Consultation')]

        response = self.query_with_token(
            self.access_token_master, edit_consultation_item.format(
                **update_data))

        self.assertNotIn('errors', response)
        self.assertEqual(
            str(message), response['data']['editConsultationItem']['message'])

    def test_edit_missing_consultation_item(self):
        consultation_id = fake.random_int()

        update_data = {
            "consultation_id": consultation_id,
            "description": fake.text(max_nb_chars=50)
        }

        message =\
            "ConsultationCatalogue with id {} does not exist.".format(
                consultation_id)

        response = self.query_with_token(
            self.access_token_master, edit_consultation_item.format(
                **update_data))

        self.assertIn('errors', response)
        self.assertEqual(
            message, response['errors'][0]['message'])

    def test_delete_consultation_item(self):
        consultation_id = self.consultation_item.id

        delete_data = {"id": consultation_id}

        message = [SUCCESS_RESPONSES[
                   "deletion_success"].format(
            self.consultation_item.consultation_name)]

        response = self.query_with_token(
            self.access_token_master, delete_consultation_item.format(
                **delete_data))

        self.assertNotIn('errors', response)
        self.assertEqual(
            str(message),
            response['data']['deleteConsultationItem']['message'])
