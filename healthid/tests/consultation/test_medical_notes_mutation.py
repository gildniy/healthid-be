from faker import Faker

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.consultation import (
    add_medical_notes)
from healthid.tests.factories import (
    ConsultationItemFactory, CustomerFactory, CustomerConsultationFactory)


fake = Faker()


class TestAddMedicalNotes(BaseConfiguration):
    def setUp(self):
        super(TestAddMedicalNotes, self).setUp()
        self.consultation_item = ConsultationItemFactory()
        self.customer_2 = CustomerFactory()
        self.customer_consultation = CustomerConsultationFactory(
            customer=self.customer_2)

        self.notes_data = {
            "consultation_id": self.customer_consultation.id,
            "consultant_name": fake.name(),
            "medical_notes": fake.text(max_nb_chars=20)
        }

    def test_add_medical_notes(self):
        response = self.query_with_token(
            self.access_token, add_medical_notes.format(
                **self.notes_data))

        self.assertNotIn('errors', response)
