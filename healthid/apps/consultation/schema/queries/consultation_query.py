import graphene

from healthid.apps.consultation.models import (
    ConsultationCatalogue)
from healthid.apps.outlets.models import Outlet
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.consultation.schema.consultation_schema import (
    ConsultationCatalogueType)
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.messages.consultation_reponses import \
    CONSULTATION_ERROR_RESPONSES
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT


class Query(graphene.ObjectType):
    consultations = graphene.List(
        ConsultationCatalogueType,
        page_number=graphene.Int(),
        page_count=graphene.Int()
    )
    consultation = graphene.Field(
        ConsultationCatalogueType,
        consultation_id=graphene.Int(),
        consultation_name=graphene.String(),
        description=graphene.String(),
        price_per_session=graphene.Int(),
        approved_delivery_format=graphene.String(),
        consultant_role=graphene.String(),
        minutes_per_session=graphene.Int()
    )
    total_consultations_pages_count = graphene.Int()
    pagination_result = None

    @login_required
    def resolve_consultations(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        user = info.context.user
        outlet = get_model_object(Outlet, 'id', user.active_outlet.id)
        business_id = outlet.business_id

        all_consultations = ConsultationCatalogue.objects.filter(
            business=business_id).order_by("id")
        if page_count or page_number:
            consultations = pagination_query(
                all_consultations, page_count, page_number)
            Query.pagination_result = consultations
            return consultations[0]
        paginated_response = pagination_query(all_consultations,
                                              PAGINATION_DEFAULT["page_count"],
                                              PAGINATION_DEFAULT["page_number"]
                                              )
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_total_consultations_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying totalConsultationsPagesCount query field should
        strictly be called after the consultations query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_consultation(self, info, **kwargs):
        consultation_id = kwargs.get("consultation_id")
        consultation = get_model_object(
            ConsultationCatalogue, 'id', consultation_id)
        user = info.context.user
        outlet = get_model_object(Outlet, 'id', user.active_outlet.id)
        business_id = outlet.business_id
        if consultation.business.id != business_id:
            consultation_query_error = \
                CONSULTATION_ERROR_RESPONSES[
                    "consultation_doesnot_exist_error"]
            raise GraphQLError(consultation_query_error)
        return consultation
