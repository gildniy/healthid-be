import graphene
from graphene_django import DjangoObjectType
from graphene.utils.resolve_only_args import resolve_only_args

from healthid.apps.consultation.models import (
    ConsultationCatalogue, CustomerConsultation, MedicalHistory)


class ConsultationCatalogueType(DjangoObjectType):
    consultant_role = graphene.String(source='get_consultant_role')

    class Meta:
        model = ConsultationCatalogue

    id = graphene.ID(required=True)

    @resolve_only_args
    def resolve_id(self):
        return self.id


class CustomerConsultationType(DjangoObjectType):
    status = graphene.String(source='get_status')

    class Meta:
        model = CustomerConsultation

    id = graphene.ID(required=True)

    @resolve_only_args
    def resolve_id(self):
        return self.id


class MedicalHistoryType(DjangoObjectType):

    class Meta:
        model = MedicalHistory
