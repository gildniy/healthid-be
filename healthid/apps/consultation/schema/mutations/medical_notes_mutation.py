import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.consultation.models import (
    MedicalHistory)
from healthid.apps.consultation.schema.consultation_schema import (
    MedicalHistoryType)
from healthid.utils.app_utils.database import (
    SaveContextManager)


class AddMedicalNotes(graphene.Mutation):
    add_notes = graphene.Field(MedicalHistoryType)

    class Arguments:
        consultation_id = graphene.Int(required=True)
        author = graphene.String(required=True)
        medical_notes = graphene.String(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        add_notes = MedicalHistory(authorized_by=user)

        for (key, value) in kwargs.items():
            setattr(add_notes, key, value)

        with SaveContextManager(add_notes, model=MedicalHistory) as add_notes:
            pass

        return AddMedicalNotes(add_notes=add_notes)
