from django.db import models
from django.db.models.signals import post_save
from healthid.apps.authentication.models import User
from healthid.models import BaseModel
from healthid.settings import pusher
from healthid.utils.app_utils.id_generator import id_gen


class Notification(BaseModel):
    '''Model to handle all notifications
    '''
    UNREAD = "unread"
    READ = "read"

    NOTIFICATION_STATUSES = (
        (UNREAD, "unread"),
        (READ, "unread"),
    )
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user', null=True)
    subject = models.TextField(null=True)
    status = models.CharField(max_length=10, choices=NOTIFICATION_STATUSES,
                              default=UNREAD)
    event_name = models.CharField(
        max_length=100, default='general_notification')

    def __str__(self):
        return self.subject

    @property
    def get_notification_meta(self):
        """
        get meta of a notification
        Returns:
            list: meta of a single notification
        """
        return NotificationMeta.objects.all().filter(notification=self.id)


class NotificationMeta(BaseModel):
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE)
    body = models.TextField()

    def __str__(self):
        return self.notification_id

    @property
    def get_notification(self):
        """
        get a notification
        Returns:
            object: a single notification
        """
        return self.notification


def save_notify(sender, instance, **kwargs):
    meta = instance
    notification = meta.get_notification
    if notification.event_name and notification.subject:
        pusher.trigger(
            'notification-channel',
            notification.event_name, {
                'subject':  notification.subject,
                'message': meta.body
            })


post_save.connect(save_notify, NotificationMeta)
