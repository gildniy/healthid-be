import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.consultation.models import ConsultationCatalogue
from healthid.apps.consultation.schema.consultation_schema import (
    ConsultationCatalogueType)

from healthid.apps.consultation.schema.mutations.\
    schedule_consultation_mutation import (BookConsultation,
                                           UpdateConsultation,
                                           DeleteBookedConsultation)
from healthid.apps.consultation.schema.mutations.\
    medical_notes_mutation import AddMedicalNotes
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class CreateConsultationItem(graphene.Mutation):
    """
    Creates consultation item for an outlet's catalogue
    Args:
        consultation_name (str) the name of the consultation
        description (str) details what the consultation is about
        outlet_id (int) id for the outlet offering the consultation
        approved_delivery_format_ids (array) ids of delivery modes
        consultant_role_id (int) id of who can perform the
            consultation
        minutes_per_session (int) estimated duration of each
            session
        price_per_session (int) price for the consultation
    returns:
         consultation object that was created,
         otherwise a GraphqlError is raised
    """

    consultation = graphene.Field(ConsultationCatalogueType)
    success = graphene.String()

    class Arguments:
        consultation_name = graphene.String(required=True)
        description = graphene.String(required=True)
        business_id = graphene.String(required=True)
        approved_delivery_formats = graphene.List(graphene.String)
        consultant_role = graphene.String()
        minutes_per_session = graphene.Int()
        price_per_session = graphene.Int(required=True)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        consultation = ConsultationCatalogue()

        params = {
            'model': ConsultationCatalogue,
            'field': 'consultation_name',
            'value': kwargs['consultation_name']
        }

        for (key, value) in kwargs.items():
            setattr(consultation, key, value)

        with SaveContextManager(consultation, **params) as consultation:
            pass

        success =\
            [SUCCESS_RESPONSES[
                'creation_success'].format(consultation.consultation_name)]

        return CreateConsultationItem(
            consultation=consultation, success=success)


class EditConsultationItem(graphene.Mutation):
    """
    Edits consultation item for an outlet's catalogue
    Args:
        consultation_name (str) the name of the consultation
        description (str) details what the consultation is about
        outlet_id (int) id for the outlet offering the consultation
        approved_delivery_format_ids (array) ids of delivery modes
        consultant_role_id (int) id of who can perform the
            consultation
        minutes_per_session (int) estimated duration of each
            session
        price_per_session (int) price for the consultation
    returns:
         consultation object that was updated and a message,
         otherwise a GraphqlError is raised
    """

    consultation = graphene.Field(ConsultationCatalogueType)
    message = graphene.String()

    class Arguments:
        consultation_id = graphene.Int(required=True)
        description = graphene.String()
        business_id = graphene.String()
        approved_delivery_formats = graphene.List(graphene.String)
        consultant_role = graphene.String()
        minutes_per_session = graphene.Int()
        price_per_session = graphene.Int()

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):

        consultation = get_model_object(
            ConsultationCatalogue, 'id', kwargs.get('consultation_id'))

        for (key, value) in kwargs.items():
            setattr(consultation, key, value)

        message =\
            [SUCCESS_RESPONSES[
                'update_success'].format('Consultation')]

        with SaveContextManager(consultation, model=ConsultationCatalogue) as consultation:  # noqa
            pass

        return EditConsultationItem(
            consultation=consultation, message=message)


class DeleteConsultationItem(graphene.Mutation):
    """
    Deletes consultation item
    Args:
        id (int) the id of the consultation
    returns:
         success message,
         otherwise a GraphqlError is raised
    """
    consultation = graphene.Field(ConsultationCatalogueType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission('Manager')
    def mutate(self, info, id):
        user = info.context.user
        consultation = get_model_object(ConsultationCatalogue, 'id', id)
        consultation.delete(user)
        message = [SUCCESS_RESPONSES[
                   "deletion_success"].format(
            consultation.consultation_name)]
        return DeleteConsultationItem(message=message)


class Mutation(graphene.ObjectType):
    create_consultation_item = CreateConsultationItem.Field()
    edit_consultation_item = EditConsultationItem.Field()
    delete_consultation_item = DeleteConsultationItem.Field()
    book_consultation = BookConsultation.Field()
    update_consultation = UpdateConsultation.Field()
    delete_booked_consultation = DeleteBookedConsultation.Field()
    add_medical_notes = AddMedicalNotes.Field()
