from faker import Faker
from datetime import date, timedelta
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.consultations import (
    retrieve_consultations)
from healthid.tests.test_fixtures.consultations import (
    retrieve_consultation,
    retrieve_booking,
    book_consultation,
    update_consultation,
    delete_booked_consultation,
    query_all_bookings,
    retrieve_paginated_consultations,
    create_consultations,
    edit_consultation_item,
    delete_consultation_item,
    add_medical_notes,
    query_all_paginated_bookings
)
from healthid.tests.factories import (
    ConsultationItemFactory, CustomerFactory, CustomerConsultationFactory,
    OutletFactory)
from healthid.utils.messages.consultation_reponses import \
    CONSULTATION_ERROR_RESPONSES

fake = Faker()


class TestQueryConsultation(BaseConfiguration):
    def setUp(self):
        super(TestQueryConsultation, self).setUp()
        self.consultation_item = ConsultationItemFactory(
            consultation_name=fake.word(),
            description=fake.text(max_nb_chars=50),
            consultant_role="Pharmacist",
            approved_delivery_formats=["Telephonic"],
            business_id=self.business.id,
            minutes_per_session=fake.random_int(min=1, max=60),
            price_per_session=fake.random_int()
        )
        self.new_outlet = OutletFactory(name=fake.word())
        self.customer_2 = CustomerFactory()
        self.customer_consultation = CustomerConsultationFactory(
            customer=self.customer_2)

    def test_user_can_retrieve_consultations(self):
        response = self.query_with_token(
            self.access_token, retrieve_consultations)
        self.assertEqual(
            response['data']['consultations'][0]['id'],
            str(self.consultation_item.id))

    def test_user_queries_from_a_different_business(self):
        self.consultation_item2 = ConsultationItemFactory(
            consultation_name=fake.word(),
            description=fake.text(max_nb_chars=50),
            consultant_role="Pharmacist",
            approved_delivery_formats=["Telephonic"],
            minutes_per_session=fake.random_int(min=1, max=60),
            price_per_session=fake.random_int()
        )
        response = self.query_with_token(
            self.access_token, retrieve_consultation.format(
                consultation_id=self.consultation_item2.id))
        expected_message = CONSULTATION_ERROR_RESPONSES[
            "consultation_doesnot_exist_error"]
        self.assertEqual(response['errors'][0]['message'], expected_message)

    def test_consultation_id_doesnot_exist(self):
        consultation_invalid_id = 0
        response = self.query_with_token(
            self.access_token, retrieve_consultation.format(
                consultation_id=consultation_invalid_id))
        expected_message = CONSULTATION_ERROR_RESPONSES["invalid_id"].format(
            consultation_invalid_id)
        self.assertIn(expected_message, response['errors'][0]['message'])

    def test_query_booking(self):
        booked_consultation = self.schedule_consultation()
        response = self.query_with_token(
            self.access_token, retrieve_booking.format(
                id=booked_consultation.id
            )
        )

        self.assertIsNotNone(response)

    def test_book_consultation(self):
        response = self.query_with_token(
            self.access_token,
            book_consultation.format(
                self.customer_consultation.customer.id,
                self.consultation_item.id,
                self.outlet.id,
                date.today() + timedelta(days=3)
            )
        )
        self.assertEqual(
            'Now',
            response['data']['bookConsultation']['bookConsultation']['status']
        )

    def test_update_consultation(self):
        response = self.query_with_token(
            self.access_token,
            update_consultation.format(
                self.customer_consultation.id,
                date.today() + timedelta(days=5)
            )
        )
        self.assertIsNotNone(response)

    def test_delete_booked_consultation(self):
        response = self.query_with_token(
            self.access_token_master,
            delete_booked_consultation.format(
                id=self.customer_consultation.id
            ))

        self.assertIn(
            'successfully',
            response['data']['deleteBookedConsultation']['message']
        )

    def test_query_paginated_consultations(self):
        response = self.query_with_token(
            self.access_token,
            retrieve_paginated_consultations,
        )

        self.assertEqual(
            1,
            response['data']['totalConsultationsPagesCount']
        )

    def test_create_consultation_item(self):
        response = self.query_with_token(
            self.access_token_master,
            create_consultations.format(
                business_id=self.business.id
            )
        )

        self.assertIn(
            'bone marrow',
            response['data']['createConsultationItem']
            ['consultation']['description']
        )

    def test_edit_consultation_item(self):
        response = self.query_with_token(
            self.access_token_master,
            edit_consultation_item.format(
                self.consultation_item.id
            )
        )

        self.assertEqual(
            f"{self.consultation_item.id}",
            response['data']['editConsultationItem']['consultation']['id']
        )

    def test_delete_consultation_item(self):
        response = self.query_with_token(
            self.access_token_master,
            delete_consultation_item.format(
                self.consultation_item.id
            )
        )

        self.assertIn(
            'deleted successfully',
            response['data']['deleteConsultationItem']['message']
        )

    def test_add_medical_notes(self):

        medical_note = 'Medical notes added'
        response = self.query_with_token(
            self.access_token_master,
            add_medical_notes.format(
                self.customer_consultation.id,
                medical_note)
        )

        self.assertEqual(
            medical_note,
            response['data']['addMedicalNotes']['addNotes']['medicalNotes']
        )

    def test_query_bookings(self):
        self.schedule_consultation()
        response = self.query_with_token(
            self.access_token_master, query_all_bookings
        )

        self.assertEqual(
            'Now',
            response['data']['bookings'][0]['status']
        )

    def test_query_paginated_bookings(self):
        self.schedule_consultation()
        response = self.query_with_token(
            self.access_token_master,
            query_all_paginated_bookings
        )

        self.assertEqual(
            'Now',
            response['data']['bookings'][0]['status']
        )
