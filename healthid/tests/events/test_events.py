from django.core.management import call_command

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.events import (business_event, delete_event,
                                                 event_type, new_event,
                                                 outlet_event, personal_event,
                                                 view_event, view_event_types,
                                                 view_events, view_wrong_event,
                                                 wrong_event_type,
                                                 wrong_user_delete_event,
                                                 wrong_user_update_event)
from healthid.utils.messages.events_responses import EVENTS_ERROR_RESPONSES


class EventTestCase(BaseConfiguration):
    """Class to test the events app
    """

    def setUp(self):
        super().setUp()
        call_command('loaddata', 'healthid/fixtures/event_types.json')

    def test_create_event(self):
        """Test that a user can create an event successfully
        """
        response = self.query_with_token(self.access_token, personal_event)

        self.assertIn('data', response)

    def test_create_event_unauthorised(self):
        """Test that a user can't create an event successfully
        """
        response = self.query_with_token(self.access_token, business_event)
        self.assertIn('errors', response)

    def test_update_event(self):
        """Test that a user can update an event sucessfully
        """
        self.query_with_token(self.access_token, personal_event)
        response = self.query_with_token(self.access_token, new_event)
        self.assertIn('data', response)

    def test_update_event_with_unauthorised_user(self):
        """Test that a user can't update an event that doesn't belong to them
        """
        event = self.query_with_token(self.access_token, personal_event)
        response = self.query_with_token(self.access_token_master,
                                         wrong_user_update_event(
                                             event['data']['createEvent'
                                                           ]['event']['id']))
        self.assertEqual(EVENTS_ERROR_RESPONSES[
                          "event_update_validation_error"],
                         response['errors'][0]['message'])

    def test_delete_event(self):
        """Test that user can delete and event
        """
        event = self.query_with_token(self.access_token, personal_event)
        response = self.query_with_token(self.access_token, delete_event(
            event['data']['createEvent']['event']['id']))
        self.assertIn('data', response)

    def test_view_events(self):
        """Test that user can view events
        """
        self.query_with_token(self.access_token, personal_event)

        response = self.query_with_token(self.access_token, view_events)
        self.assertIn('data', response)

    def test_view_single_event(self):
        """Test that user can view a single event
        """
        event = self.query_with_token(self.access_token, personal_event)
        response = self.query_with_token(self.access_token, view_event(
            event['data']['createEvent']['event']['id']))
        self.assertIn('data', response)

    def test_view_single_event_invalid_id(self):
        """Test that user cannot an event that doesn't exist
        """
        self.query_with_token(self.access_token, personal_event)

        response = self.query_with_token(self.access_token, view_wrong_event)
        self.assertIn('errors', response)

    def test_delete_event_with_unauthorised_user(self):
        """Test that a user can't delete an event that doesn't belong to them
        """
        event = self.query_with_token(self.access_token, personal_event)
        response = self.query_with_token(self.access_token_master,
                                         wrong_user_delete_event(
                                             event['data']['createEvent'
                                                           ]['event']['id']))

        self.assertEqual(EVENTS_ERROR_RESPONSES[
                         "event_delete_validation_error"],
                         response['errors'][0]['message'])

    def test_create_outlet_event_unauthorised(self):
        """Test that a user can't create an event successfully
        """
        response = self.query_with_token(self.access_token, outlet_event)
        self.assertIn('errors', response)

    def test_create_event_type(self):
        """Test that user can create event types
        """
        response = self.query_with_token(self.access_token_master, event_type)
        self.assertEqual(
            response['data']['createEventType']['eventType']['name'],
            'Test Personal')

    def test_view_event_types(self):
        """Test that user can view event types
        """
        response = self.query_with_token(self.access_token, view_event_types)
        self.assertIn('data', response)

    def test_create_event_wrong_event_type(self):
        """Test that a user can't create and event with wrong event type
        """
        response = self.query_with_token(self.access_token, wrong_event_type)
        self.assertIn(response['errors'][0]['message'],
                      EVENTS_ERROR_RESPONSES[
                       "inexistent_event_type"].format("f36bw1"))
