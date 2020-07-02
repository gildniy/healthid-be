import graphene

from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.orders.models import Suppliers
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class DeleteSupplier(graphene.Mutation):
    """
    Delete a supplier

    args:
        id(str): id of the supplier to be deleted

    returns:
        success(str): success message confirming deleted supplier
    """

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Field(graphene.String)

    @classmethod
    @user_permission('Operations Admin')
    def mutate(cls, root, info, id):
        supplier = get_model_object(Suppliers, 'id', id)
        name = supplier.name
        supplier.delete()
        success = SUCCESS_RESPONSES[
            "deletion_success"].format("Supplier" + name)
        return cls(success=success)
