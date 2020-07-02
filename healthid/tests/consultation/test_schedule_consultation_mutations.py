from faker import Faker

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.consultation import (
    book_consultation, update_consultation, delete_consultation)
from healthid.utils.messages.consultation_reponses import\
    CONSULTATION_SUCCESS_RESPONSES
from healthid.tests.factories import (
    ConsultationItemFactory, CustomerFactory, CustomerConsultationFactory,
    OutletFactory)


fake = Faker()


class TestScheduleConsultation(BaseConfiguration):
    """
    Tests creating, updating, and deleting a consultation booking
    """

    def setUp(self):
        super(TestScheduleConsultation, self).setUp()

        self.customer_2 = CustomerFactory()
        self.customer_consultation = CustomerConsultationFactory(
            customer=self.customer_2)
        self.outlet = OutletFactory()
        self.consultation_item = ConsultationItemFactory(
            business=self.outlet.business)

        self.booking_data = {
            "customer_id": self.customer_2.id,
            "consultation_type_id": self.consultation_item.id,
            "status": "Now",
            "outlet_id": self.outlet.id,
        }

    def test_book_consultation(self):
        response = self.query_with_token(
            self.access_token, book_consultation.format(**self.booking_data))

        success =\
            CONSULTATION_SUCCESS_RESPONSES["consultation_schedule_success"]

        self.assertNotIn('errors', response)
        self.assertEqual(
            success, response['data']['bookConsultation']['success'])
        self.assertEqual(
            'Consultation', response['data']['bookConsultation']
            ['bookConsultation']['event']['eventType']['name'])

    def test_update_booked_consultation(self):
        consultation_id = self.customer_consultation.id

        update_data = {
            "consultation_id": consultation_id,
            "status": "Later"
        }
        success =\
            CONSULTATION_SUCCESS_RESPONSES["consultation_schedule_success"]

        response = self.query_with_token(
            self.access_token, update_consultation.format(**update_data))

        self.assertNotIn('errors', response)
        self.assertEqual(
            success, response['data']['updateConsultation']['success'])

    def test_delete_booked_consultation(self):
        delete_data = {
            "consultation_id": self.customer_consultation.id
        }

        message =\
            CONSULTATION_SUCCESS_RESPONSES['delete_booking'].format(
                self.customer_consultation.customer)

        response = self.query_with_token(
            self.access_token_master, delete_consultation.format(
                **delete_data))

        self.assertNotIn('errors', response)
        self.assertEqual(
            message, response['data']['deleteBookedConsultation']['message'])
