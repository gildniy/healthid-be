import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.notifications.models import Notification, NotificationMeta
from graphql import GraphQLError
from healthid.utils.messages.notifications_responses import\
    NOTIFICATION_ERROR_RESPONSES


class NotificationMetaType(DjangoObjectType):
    class Meta:
        model = NotificationMeta


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification

    notification_meta = graphene.List(NotificationMetaType)

    def resolve_notification_meta(self, info, **kwargs):
        """
        get meta data of a notification
        Returns:
            list: meta data of a single notification
        """
        return self.get_notification_meta


class Query(graphene.ObjectType):
    """
    Queries notification messages where the user is a recipient

    returns:
        notifications: list of 'Notification' objects
    """
    notifications = graphene.List(NotificationType, status=graphene.String())

    @login_required
    def resolve_notifications(self, info, **kwargs):
        user = info.context.user
        status = kwargs.get('status')
        notifications = Notification.objects.filter(
            user=user, status__iexact=status) \
            if status else Notification.objects.filter(user=user)
        if notifications:
            return notifications
        raise GraphQLError(NOTIFICATION_ERROR_RESPONSES["empty_notifications"])
