import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import SupplierNote
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES


class DeleteSupplierNote(graphene.Mutation):
    """
    Delete a supplier note

    args:
        id(int): id of the note to delete

    returns:
        success(str): success message confirming note delete
        id(int)): id of the deleted note
    """

    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, id):
        user = info.context.user
        supplier_note = get_model_object(SupplierNote, "id", id)
        if info.context.user != supplier_note.user:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES[
                    "supplier_note_deletion_validation_error"])
        supplier_note.delete(user)
        return DeleteSupplierNote(
            success=SUCCESS_RESPONSES[
                "deletion_success"].format("Supplier's note"))
