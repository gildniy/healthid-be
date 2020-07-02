from django.conf import settings
from django.core.mail import EmailMessage
from healthid.apps.authentication.models import User
from healthid.apps.despatch_queue.models import DespatchQueue, Despatch_Meta
from healthid.utils.app_utils.database import SaveContextManager
from django.template.loader import render_to_string
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.date_utils.is_same_date import (
    is_same_date, remove_microseconds, remove_seconds)
from smtplib import (
    SMTPException, SMTPAuthenticationError,
    SMTPServerDisconnected, SMTPConnectError)
import threading
from django.utils import timezone


def notify(users, **kwargs):
    '''Function to notify the users
    through email notifications
    '''
    despatch = {}
    despatch_queues = []
    for user in users:
        despatch_queue = DespatchQueue.objects.create(
            recipient=user,
            due_date=kwargs.get('due_date')
        )
        with SaveContextManager(despatch_queue, model=DespatchQueue)\
                as d_queue:
            body = kwargs.get('body')
            subject = kwargs.get('subject')
            for (key, value) in kwargs.items():
                if key != 'due_date':
                    despatch = Despatch_Meta(
                        dataKey=key, dataValue=value, despatch=d_queue)
                    despatch.save()
            if is_same_date(
                    remove_seconds(d_queue.due_date),
                    timezone.localtime(
                        remove_seconds(
                            remove_microseconds(timezone.now())))):
                thread = threading.Thread(target=send_email_notifications(
                    subject,
                    user,
                    body, d_queue))
                thread.start()
            despatch_queues.append(d_queue)
    return despatch_queues


def queue_emails_job():
    email_parts = {}
    try:
        despatch_queue = DespatchQueue.objects.all()
        despatch_queue_meta = Despatch_Meta.objects.all()
        if len(despatch_queue) > 0:
            for despatch_q in despatch_queue:
                id = despatch_q.recipient_id
                if timezone.localtime(remove_seconds(despatch_q.due_date)) <= \
                    timezone.localtime(
                    remove_seconds(remove_microseconds(timezone.now()))) and \
                        despatch_q.status == 'pending':
                    email_part = get_model_object(User, 'id', id)
                    for despatch_meta in despatch_queue_meta:
                        if despatch_meta.__dict__['despatch_id'] ==\
                                despatch_q.__dict__['id']:
                            email_parts['email'] = email_part
                            email_parts[despatch_meta.__dict__['dataKey']
                                        ] = despatch_meta.__dict__['dataValue']
                    if email_parts:
                        send_email_notifications(
                            email_parts['subject'],
                            email_parts['email'],
                            email_parts['body'], despatch_q)
    except Exception:
        pass


def change_send_status(d_queue, status):
    '''Function to change received status
    '''
    d_queue.status = status
    with SaveContextManager(d_queue, model=DespatchQueue):
        return


def send_email_notifications(subject, user, body, despatch_meta):
    '''Function to send email notifications
    '''
    template = \
        'email_alerts/email_base.html'
    subject = subject
    context = {
        'template_type': 'Email Notification',
        'small_text_detail': body,
    }
    if user.email_notification_permissions and body:
        html_body = render_to_string(
            template,
            context
        )
        try:
            email = EmailMessage(subject=subject,
                                 body=html_body,
                                 from_email=settings.DEFAULT_FROM_EMAIL,
                                 to=[str(user.email)])
            email.content_subtype = 'html'
            is_sent = email.send()
            if is_sent == 1:
                change_send_status(despatch_meta, 'sent')
        except (
                SMTPAuthenticationError,
                SMTPServerDisconnected,
                SMTPConnectError):
            change_send_status(despatch_meta, 'pending')
        except SMTPException:
            change_send_status(despatch_meta, 'failed')
        else:
            change_send_status(despatch_meta, 'sent')
