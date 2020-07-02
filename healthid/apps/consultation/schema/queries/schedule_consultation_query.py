import graphene

from healthid.apps.consultation.schema.consultation_schema import (
    CustomerConsultationType)
from healthid.apps.consultation.schema.consultation_schema import (
    CustomerConsultation)
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.messages.consultation_reponses import \
    CONSULTATION_ERROR_RESPONSES
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT
from healthid.utils.app_utils.database import get_model_object


class Query(graphene.ObjectType):
    bookings = graphene.List(CustomerConsultationType,
                             pageNumber=graphene.Int(),
                             pageCount=graphene.Int())
    booking = graphene.Field(
        CustomerConsultationType,
        id=graphene.Int(),
        customer_id=graphene.Int(),
        booked_by_id=graphene.String(),
        status=graphene.String(),
        consultation_type_id=graphene.Int(),
        consultant=graphene.String(),
        booking_date=graphene.Date()
    )
    total_bookings_pages_count = graphene.Int()
    pagination_result = None

    @login_required
    def resolve_bookings(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        user_outlet = info.context.user.active_outlet.id
        all_customer_consultations = CustomerConsultation.objects.filter(
            outlet_id=user_outlet).order_by("id")

        if len(all_customer_consultations) > 0:
            if page_count or page_number:
                customer_consultations = pagination_query(
                    all_customer_consultations, page_count, page_number)
                Query.pagination_result = customer_consultations
                return customer_consultations[0]
            paginated_response =\
                pagination_query(all_customer_consultations,
                                 PAGINATION_DEFAULT["page_count"],
                                 PAGINATION_DEFAULT["page_number"]
                                 )
            Query.pagination_result = paginated_response
            return paginated_response[0]
        error = CONSULTATION_ERROR_RESPONSES["no_scheduled_consultations"]
        raise GraphQLError(error)

    @login_required
    def resolve_total_bookings_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying totalBookingsPagesCount query field should
        strictly be called after the bookings query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_booking(self, info, **kwargs):
        customer_id = kwargs.get("id")
        user = info.context.user
        if customer_id > 0:
            booking = get_model_object(
                CustomerConsultation, 'id', customer_id)
            if booking.outlet.id != user.active_outlet.id:
                error = CONSULTATION_ERROR_RESPONSES["schedule_error"]
                raise GraphQLError(error)
            return booking
        customer = CONSULTATION_ERROR_RESPONSES["invalid_id"].format("Booking")
        raise GraphQLError(customer)
