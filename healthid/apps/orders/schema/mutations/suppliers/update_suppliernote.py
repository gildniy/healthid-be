import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import SupplierNote
from healthid.apps.outlets.models import Outlet
from healthid.apps.orders.schema.suppliers_query import SupplierNoteType
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.validators import special_cahracter_validation
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES


class UpdateSupplierNote(graphene.Mutation):
    """
    Update a supplier note

    args:
        supplier_id(str): id of the supplier of note
        outlet_ids(list): outlets that source products from the supplier
        note(str): text to update supplier note with

    returns:
        success(str): success message confirming note update
        supplier_note(obj): 'SupplierNote' model object detailing the
                            updated note
    """

    class Arguments:
        id = graphene.Int(required=True)
        supplier_id = graphene.String()
        outlet_ids = graphene.List(graphene.Int)
        note = graphene.String()

    success = graphene.Field(graphene.String)
    supplier_note = graphene.Field(SupplierNoteType)

    @classmethod
    @login_required
    @user_permission('Operations Admin')
    def mutate(cls, root, info, id, **kwargs):
        outlet_ids = kwargs.pop('outlet_ids')
        supplier_note = get_model_object(SupplierNote, "id", id)
        if info.context.user != supplier_note.user:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES[
                    "supplier_note_update_validation_error"])
        for key, value in kwargs.items():
            if key in ["note"]:
                special_cahracter_validation(value)
                if len(value.split()) < 2:
                    raise GraphQLError(
                        ORDERS_ERROR_RESPONSES["supplier_note_length_error"])
            setattr(supplier_note, key, value)

        if outlet_ids:
            outlets = [get_model_object(Outlet, 'id', outlet_id)
                       for outlet_id in outlet_ids]
            supplier_note.outlet.clear()
            supplier_note.outlet.add(*outlets)
        with SaveContextManager(supplier_note) as supplier_note:
            return cls(
                success=SUCCESS_RESPONSES[
                    "update_success"].format("Supplier's note"),
                supplier_note=supplier_note)
