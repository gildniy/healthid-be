import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers, SupplierNote
from healthid.apps.outlets.models import Outlet
from healthid.apps.orders.schema.suppliers_query import (
    SuppliersType, SupplierNoteType)
from healthid.utils.app_utils.validator import validator
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)


class CreateSupplierNote(graphene.Mutation):
    """
    Create a note for a particular supplier

    args:
        supplier_id(str): id of the supplier of note
        outlet_ids(list): outlets that source products from the supplier
        note(str): note to create for the supplier

    returns:
        message(str): success message confirming note creation
        supplier_note(obj): 'SupplierNote' model object detailing the
                            created note
        supplier(obj): 'Suppliers' model object detailing the noted supplier
    """

    class Arguments:
        supplier_id = graphene.String(required=True)
        outlet_ids = graphene.List(graphene.Int, required=True)
        note = graphene.String(required=True)

    message = graphene.Field(graphene.String)
    supplier_note = graphene.Field(SupplierNoteType)
    supplier = graphene.Field(SuppliersType)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        supplier_id = kwargs.get("supplier_id")
        user = info.context.user
        outlet_ids = kwargs.get("outlet_ids")
        note = kwargs.get("note")
        validator.special_character_validation(note)
        if len(note.split()) < 2:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES["supplier_note_length_error"])
        supplier = get_model_object(Suppliers, "id", supplier_id)
        outlets = [get_model_object(Outlet, 'id', outlet_id)
                   for outlet_id in outlet_ids]
        supplier_note = SupplierNote(supplier=supplier, note=note, user=user)
        with SaveContextManager(supplier_note) as supplier_note:
            supplier_note.outlet.add(*outlets)
            supplier_note.save()
            return cls(
                supplier_note=supplier_note,
                supplier=supplier,
                message=SUCCESS_RESPONSES[
                    "creation_success"].format("Supplier's note"))
