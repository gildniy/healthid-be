import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.events.models import Event
from healthid.apps.events.models import EventType as EventTypeModel
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.events_responses import EVENTS_ERROR_RESPONSES
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT


class EventsType(DjangoObjectType):
    class Meta:
        model = Event


class EventTypeType(DjangoObjectType):

    class Meta:
        model = EventTypeModel


class Query(graphene.ObjectType):
    """
    Queries events for the outlet a user belongs to

    returns:
        list of event of objects: if 'events' is queried
        a single 'EventsType' object: if 'event' is queried
    """
    events = graphene.List(EventsType, page_count=graphene.Int(),
                           page_number=graphene.Int())
    event = graphene.Field(
        EventsType,
        id=graphene.String(),
        business=graphene.String(),
        outlet=graphene.String(),
        event_type=graphene.String(),
        event_title=graphene.String(),
        start=graphene.Date(),
        end=graphene.Date(),
        description=graphene.String()
    )
    event_types = graphene.List(EventTypeType)
    total_events_pages_count = graphene.Int()
    pagination_result = None

    @login_required
    def resolve_events(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        events_set = Event.objects.filter(
                                   Q(user=user) | Q(outlet=outlet)
                                   ).order_by('id')
        if page_count or page_number:
            events = pagination_query(
                events_set, page_count, page_number)
            Query.pagination_result = events
            return events[0]
        if events_set:
            paginated_response = pagination_query(events_set,
                                                  PAGINATION_DEFAULT[
                                                      "page_count"],
                                                  PAGINATION_DEFAULT[
                                                      "page_number"])
            Query.pagination_result = paginated_response
            return paginated_response[0]
        return GraphQLError(EVENTS_ERROR_RESPONSES["no_events_error"])

    @login_required
    def resolve_total_events_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying totalEventsPagesCount query field should
        strictly be called after the events query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_event(self, info, **kwargs):
        id = kwargs.get('id')
        event = get_model_object(Event, 'id', id)
        return event

    @login_required
    def resolve_event_types(self, info, **kwargs):
        return EventTypeModel.objects.all()
