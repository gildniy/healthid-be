from django.conf import settings
from django.core.mail import EmailMessage


def send_email_notifications(user, product, html_body):
    '''Function to send email notifications
    '''
    if user.email_notification_permissions:
        email = EmailMessage(subject='Expired Products!',
                             body=html_body,
                             from_email=settings.DEFAULT_FROM_EMAIL,
                             to=[str(user.email)])

        email.content_subtype = 'html'
        email.send()
