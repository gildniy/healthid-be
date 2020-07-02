from django.conf import settings
from django.core.mail import EmailMessage
from healthid.apps.notifications.models import Notification, NotificationMeta
from healthid.utils.app_utils.database import SaveContextManager
from django.template.loader import render_to_string


def notify(users, subject, body, event_name=None,
           html_subject=None, html_body=None):
    '''
    Function to notify the appropriate user
    '''
    notifications = []
    for user in users:
        notification = Notification(subject=str(subject),
                                    user=user,
                                    event_name=event_name
                                    or Notification().event_name)

        with SaveContextManager(notification) as notification:
            notification_meta = NotificationMeta.objects.create(
                notification_id=notification.id,
                body=str(body))

            notification.notification_meta = notification_meta
            notifications.append(notification)

            if html_subject and html_body:
                send_email_notifications(html_subject, user, html_body)
    return notifications


def send_email_to(subject, email, html_body=None):
    """
    Send email to given address
    """
    email = EmailMessage(
        subject=subject,
        body=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email]
    )
    email.content_subtype = 'html'
    email.send()


def send_email_notifications(subject, user, html_body=None):
    '''Function to send email notifications
    '''
    if user.email_notification_permissions and html_body:
        html = render_to_string(
            html_body,
            subject
        )
        email = EmailMessage(subject=subject,
                             body=html,
                             from_email=settings.DEFAULT_FROM_EMAIL,
                             to=[str(user.email)])

        email.content_subtype = 'html'
        email.send()
