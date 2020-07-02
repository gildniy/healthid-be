import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers
from healthid.apps.orders.schema.suppliers_query import SuppliersType
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES


class EditProposal(graphene.Mutation):
    """
    Edit a proposed supplier's details

    args:
        id(str): id of the supplier to be edited
        name(str): supplier name
        tier_id(int): id of the supplier's category

    returns:
        edit_request(obj): 'Suppliers' model object detailing the edit request
        message(str): success message confirming supplier edit
    """

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        tier_id = graphene.Int()

    edit_request = graphene.Field(SuppliersType)
    message = graphene.Field(graphene.String)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')
        proposed_edit = get_model_object(Suppliers, 'id', id)
        if proposed_edit.user != info.context.user:
            msg = ORDERS_ERROR_RESPONSES["edit_proposal_validation_error"]
            raise GraphQLError(msg)
        kwargs.pop('id')
        for (key, value) in kwargs.items():
            if key is not None:
                setattr(proposed_edit, key, value)
        params = {'model': Suppliers}
        with SaveContextManager(proposed_edit, **params) as edit_request:
            name = proposed_edit.parent.name
            msg = SUCCESS_RESPONSES["update_success"].format("Supplier" + name)
            return cls(edit_request, msg)
