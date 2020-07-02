from dateutil import parser

from django.utils.timezone import make_aware

import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.consultation.models import (
    CustomerConsultation, ConsultationCatalogue)
from healthid.apps.outlets.models import Outlet
from healthid.apps.consultation.schema.consultation_schema import (
    CustomerConsultationType)
from healthid.apps.events.models import Event, EventType
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.consultation_reponses import (
    CONSULTATION_SUCCESS_RESPONSES, CONSULTATION_ERROR_RESPONSES)


class BookConsultation(graphene.Mutation):
    """
    Books consultation for a customer
    Args:
        customer_id (int) id of customer booking the consultation
        consultation_type_id (int) id of consultation item
        consultant (str) name of consultant
        status (str) status of the consultation
        booking_date (str) date set for the consultation
    returns:
         consultation object that was created and success message,
         otherwise a GraphqlError is raised
    """
    book_consultation = graphene.Field(CustomerConsultationType)
    success = graphene.String()

    class Arguments:
        customer_id = graphene.Int(required=True)
        consultation_type_id = graphene.Int(required=True)
        outlet_id = graphene.Int(required=True)
        consultant = graphene.String()
        status = graphene.String()
        booking_date = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        book_consultation = CustomerConsultation(booked_by=user)
        consultation_type_id = kwargs.get('consultation_type_id')
        outlet_id = kwargs.get('outlet_id')
        booking_date = kwargs.get('booking_date')

        consultation_catalogue_item = get_model_object(
            ConsultationCatalogue, 'id', consultation_type_id)
        outlet = get_model_object(Outlet, 'id', outlet_id)

        if consultation_catalogue_item.business.id != outlet.business.id:
            outlet_error = CONSULTATION_ERROR_RESPONSES["outlet_error"]
            raise GraphQLError(outlet_error)

        if booking_date:
            booking_date = parser.parse(booking_date)
            kwargs['booking_date'] = make_aware(booking_date)

        for (key, value) in kwargs.items():
            if key in ('customer_id', 'consultation_type_id',
                       'outlet_id') and \
                    str(value).strip() == "":
                raise GraphQLError(
                    'The {} field cannot be empty'.format(key))
            setattr(book_consultation, key, value)

        success =\
            CONSULTATION_SUCCESS_RESPONSES["consultation_schedule_success"]

        with SaveContextManager(book_consultation, model=CustomerConsultation) as book_consultation:  # noqa
            booking_date = book_consultation.booking_date
            description = \
                book_consultation.consultation_type.consultation_name
            event_type = EventType.objects.get_or_create(
                name='Consultation')
            event = Event(
                start_date=booking_date.date(),
                end_date=booking_date.date(),
                start_time=booking_date.time(),
                end_time=book_consultation.end_time.time(),
                event_title=f'Consultation for \
                {book_consultation.customer.first_name}',
                description=f'{description}',
                event_type=event_type[0])
            event.save()
            book_consultation.event = event
            book_consultation.save()

        return BookConsultation(book_consultation=book_consultation,
                                success=success)


class UpdateConsultation(graphene.Mutation):
    """
    Edits booked consultation
    Args:
        consultation_id (int) id of the booked consultation
        status (str) new status of the consultation
        consultant (str) name of new consultant
        booking_date (str) new booking date
        paid (bool) payment status
    returns:
         consultation object that was updated and a message,
         otherwise a GraphqlError is raised
    """
    update_consultation = graphene.Field(CustomerConsultationType)
    success = graphene.String()

    class Arguments:
        consultation_id = graphene.Int(required=True)
        status = graphene.String()
        consultant = graphene.String()
        booking_date = graphene.String()
        paid = graphene.Boolean()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        update_consultation = get_model_object(
            CustomerConsultation, 'id', kwargs.get('consultation_id'))

        update_consultation.updated_by = user

        booking_date = kwargs.get('booking_date')

        if booking_date:
            booking_date = parser.parse(booking_date)
            kwargs['booking_date'] = make_aware(booking_date)

        for (key, value) in kwargs.items():
            setattr(update_consultation, key, value)

        with SaveContextManager(update_consultation, model=CustomerConsultation) as update_consultation:  # noqa
            pass

        if booking_date:
            new_date = update_consultation.booking_date
            event = get_model_object(Event, 'id', update_consultation.event_id)
            event_data = {
                'start_date': new_date.date(),
                'end_date': new_date.date(),
                'start_time': new_date.time(),
                'end_time': update_consultation.end_time.time()}

            for (key, value) in event_data.items():
                setattr(event, key, value)

            with SaveContextManager(event, model=Event) as event:
                pass

        success =\
            CONSULTATION_SUCCESS_RESPONSES["consultation_schedule_success"]

        return UpdateConsultation(
            update_consultation=update_consultation, success=success)


class DeleteBookedConsultation(graphene.Mutation):
    """
    Deletes a scheduled consultation
    Args:
        id (int) the id of the booked consultation
    returns:
         success message,
         otherwise a GraphqlError is raised
    """
    booked_consultation = graphene.Field(CustomerConsultationType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission('Manager')
    def mutate(self, info, id):
        user = info.context.user
        booked_consultation = get_model_object(CustomerConsultation, 'id', id)
        booked_consultation.delete(user)
        message = CONSULTATION_SUCCESS_RESPONSES['delete_booking'].format(
            booked_consultation.customer)
        return DeleteBookedConsultation(message=message)
