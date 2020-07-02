import graphene
from graphql_jwt.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from healthid.apps.authentication.models import User
from healthid.apps.notifications.models import Notification
from healthid.apps.notifications.schema.notification_queries import \
    NotificationType
from healthid.utils.messages.notifications_responses import\
    NOTIFICATION_ERROR_RESPONSES, NOTIFICATION_SUCCESS_RESPONSES
from healthid.utils.notifications_utils.handle_notifications import notify
from healthid.utils.app_utils.database import get_model_object


class CreateNotification(graphene.Mutation):
    """
    Mutation used to create notification(s)
    args:
        user_ids(list): a list of user IDs
        subject(str): subject of the notification
        body(str): the content of the notification or the message
        event_name(str): the name of the event to emit

    returns:
        notification(obj): 'Notification' model object
                                detailing the created notification.
    """

    notifications = graphene.Field(graphene.List(of_type=NotificationType))
    success = graphene.Field(graphene.String)
    error = graphene.Field(graphene.String)

    class Arguments:
        user_ids = graphene.List(required=True, of_type=graphene.String)
        subject = graphene.String(required=True)
        body = graphene.String()
        event_name = graphene.String()

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        user_ids = kwargs.get('user_ids')
        subject = kwargs.get('subject')
        event_name = kwargs.get('event_name')
        body = kwargs.get('body')
        users = list(map(lambda user_id: get_model_object(
            User, 'id', user_id), user_ids))

        notifications = notify(
            users=users,
            subject=subject,
            event_name=event_name,
            body=body)

        return cls(notifications=notifications)


class UpdateNotificationStatus(graphene.Mutation):
    """
    Mutation used to mark a notification as read or unread.
    """

    notification = graphene.Field(NotificationType)
    success = graphene.Field(graphene.String)
    error = graphene.Field(graphene.String)

    class Arguments:
        id = graphene.String(required=True)
        status = graphene.String()

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        notification_id = kwargs.get('id')
        status = kwargs.get('status') or 'read'

        try:
            notification = Notification.objects.get(
                id=notification_id, user_id=user.id)
        except ObjectDoesNotExist:
            return cls(
                error=NOTIFICATION_ERROR_RESPONSES[
                    'notification_validation_error']
            )

        notification.status = status
        notification.save()
        success = NOTIFICATION_SUCCESS_RESPONSES["notification_toggle"].format(
            status)

        return cls(notification=notification,
                   success=success)


class DeleteNotification(graphene.Mutation):
    """
    Mutation class to delete a notification.
    """
    success = graphene.Field(graphene.String)
    error = graphene.String()

    class Arguments:
        id = graphene.String(required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        user = info.context.user
        notification_id = kwargs.get('id')

        try:
            notification = Notification.objects.get(
                id=notification_id, user_id=user.id)
        except ObjectDoesNotExist:
            return cls(
                error=NOTIFICATION_ERROR_RESPONSES[
                    "notification_validation_deletion_error"]
            )

        notification.delete()
        success = (NOTIFICATION_SUCCESS_RESPONSES[
            "notification_deletion_success"].format(
                notification_id))

        return cls(success=success)


class Mutation(graphene.ObjectType):
    create_notification = CreateNotification.Field()
    update_notification_status = UpdateNotificationStatus.Field()
    delete_notification = DeleteNotification.Field()
