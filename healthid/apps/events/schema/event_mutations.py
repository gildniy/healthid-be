import graphene
from datetime import datetime
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.events.models import Event
from healthid.apps.events.models import EventType as EventTypeModel
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.events_utils.validate_role import ValidateAdmin
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.events_responses import EVENTS_ERROR_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet


class EventType(DjangoObjectType):
    class Meta:
        model = Event


class EventsTypeType(DjangoObjectType):
    class Meta:
        model = EventTypeModel


class CreateEvent(graphene.Mutation):
    """Mutation creates an event on a calendar.
    """
    event = graphene.Field(EventType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        event_type_id = graphene.String(required=True)
        start_date = graphene.Date()
        end_date = graphene.Date(required=True)
        start_time = graphene.Time()
        end_time = graphene.Time(required=True)
        event_title = graphene.String(required=True)
        description = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        event_type = kwargs.get('event_type')
        event_type_id = kwargs.get('event_type_id')
        event_type = get_model_object(EventTypeModel, 'id', event_type_id)
        ValidateAdmin().validate_master_admin(user, event_type.name)
        event = Event(
            event_type_id=kwargs.get('event_type_id'),
            start_date=kwargs.get('start_date', datetime.today().date()),
            end_date=kwargs.get('end_date'),
            start_time=kwargs.get(
                'start_time', datetime.now().time().strftime("%H:%M:%S")),
            end_time=kwargs.get('end_time'),
            event_title=kwargs.get('event_title'),
            description=kwargs.get('description')
        )
        with SaveContextManager(event) as event:
            event.user.add(user)
            event.outlet.add(outlet)
            event.save()
            success = SUCCESS_RESPONSES["creation_success"].format("Event")
            return CreateEvent(event=event, success=success)


class UpdateEvent(graphene.Mutation):
    """Mutation updates an event on a calendar.
    """
    event = graphene.Field(EventType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        id = graphene.String(required=True)
        event_type_id = graphene.String()
        start_date = graphene.Date()
        end_date = graphene.Date()
        start_time = graphene.Time()
        end_time = graphene.Time()
        event_title = graphene.String()
        description = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        request_user = info.context.user
        _id = kwargs['id']
        event = get_model_object(Event, 'id', _id)
        event_creator = event.user.first()
        if str(request_user.email) != str(event_creator.email):
            authorization_error =\
                EVENTS_ERROR_RESPONSES["event_update_validation_error"]
            raise GraphQLError(authorization_error)
        new_event = kwargs.items()

        for key, value in new_event:
            if key is not None:
                setattr(event, key, value)
        event.save()
        success = SUCCESS_RESPONSES["update_success"].format("Event")
        return UpdateEvent(event=event, success=success)


class DeleteEvent(graphene.Mutation):
    """Deletes an event
    """
    event = graphene.Field(EventType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        id = graphene.String()

    @login_required
    def mutate(self, info, id):
        request_user = info.context.user
        event = get_model_object(Event, 'id', id)
        event_creator = event.user.first()
        if request_user != event_creator:
            delete_error =\
                EVENTS_ERROR_RESPONSES["event_delete_validation_error"]
            raise GraphQLError(delete_error)
        event.delete(request_user)
        success = SUCCESS_RESPONSES["deletion_success"].format("Event")
        return DeleteEvent(success=success)


class CreateEventType(graphene.Mutation):
    '''Mutation to create an event type
    '''
    event_type = graphene.Field(EventsTypeType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        name = graphene.String(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, name):
        params = {'model': 'EventType'}
        event_type = EventTypeModel(name=name)
        with SaveContextManager(event_type, **params) as event_type:
            success =\
                SUCCESS_RESPONSES["creation_success"].format("Event type")
            return CreateEventType(
                success=success, event_type=event_type
            )


class Mutation(graphene.ObjectType):
    create_event = CreateEvent.Field()
    delete_event = DeleteEvent.Field()
    update_event = UpdateEvent.Field()
    create_event_type = CreateEventType.Field()
