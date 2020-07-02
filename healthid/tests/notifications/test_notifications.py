from healthid.tests.base_config import BaseConfiguration
from healthid.apps.notifications.models import Notification
from healthid.tests.test_fixtures.batch_info import batch_info_query
from healthid.tests.test_fixtures.notifications import (
    delete_notification, update_notification_status, view_notifications)


class NotificationTests(BaseConfiguration):
    """
    Class to test app notifications
    """

    def setUp(self):
        super().setUp()
        self.batch_data = {
            'product_id': self.product.id,
            'supplier_id': self.supplier.id,
            'expiry_date': '2020-02-10',
        }
        self.query_with_token(
            self.access_token_master, batch_info_query.format(
                **self.batch_data))
        self.response = self.query_with_token(
            self.access_token_master, view_notifications)
        self.id = self.response['data']['notifications'][0]['id']
        self.non_existent_id = "ThanosSnapped123"

    def test_get_all_notifications(self):
        """
        Method to check if all available notifications
        can be fetched by user.
        """
        notifications_count = len(self.response['data']['notifications'])
        self.assertGreaterEqual(notifications_count, 1)

    def test_create_low_quantity_notification(self):
        """
        Method to test if a notification can be created for
        low quantity products in a batch.
        """
        subject = self.response['data']['notifications'][0]['subject']
        message = self.response['data']['notifications'][0][
            'notificationMeta'][0]['body']

        self.assertIn('Low quantity alert', subject)
        self.assertIn(self.product.product_name, message)

    def test_mark_notification_as_read(self):
        """
        Method to test if a notification can be marked as
        read.
        """
        status_response = self.query_with_token(
            self.access_token, update_notification_status.format(
                notification_id=self.notification.id))
        message = status_response['data'][
            'updateNotificationStatus']['success']
        self.assertIn('Notification was marked as read', message)

    def test_delete_notification(self):
        """
        Method to test if a notification can be deleted
        """
        response = self.query_with_token(
            self.access_token, delete_notification.format(
                notification_id=self.notification.id))
        message = response['data']['deleteNotification']['success']
        self.assertIn('was successfully deleted', message)

    def test_delete_non_existent(self):
        """
        Method to test if a non-existent
        notification can be deleted.
        """
        response = self.query_with_token(
            self.access_token, delete_notification.format(
                notification_id=self.non_existent_id))

        error = response['data']['deleteNotification']['error']
        self.assertIn('cannot delete this notification', error)

    def test_mark_non_existent_as_read(self):
        """
        Method to check for error message returned
        when a non-existent id is supplied when
        marking as read.
        """
        status_response = self.query_with_token(
            self.access_token, update_notification_status.format(
                notification_id=self.non_existent_id))

        error = status_response['data']['updateNotificationStatus']['error']
        self.assertIn('are not among the recipients', error)

    def test_no_notification(self):
        """
        Test that an error message is returned
        when there are no notifications.
        """
        # delete existing notification
        Notification.objects.all().delete()

        response = self.query_with_token(self.access_token, view_notifications)
        self.assertIn('no notifications', response['errors'][0]['message'])
