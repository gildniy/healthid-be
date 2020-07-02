import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.products.models import DispensingSize
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission

from .product_query import DispensingSizeType
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES


class CreateDispensingSize(graphene.Mutation):
    """
        Mutation to create a Dispensing Size
    """
    dispensing_size = graphene.Field(DispensingSizeType)

    class Arguments:
        name = graphene.String(required=True)

    message = graphene.List(graphene.String)

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError(PRODUCTS_ERROR_RESPONSES["invalid_input_error"])
        dispensing_size = DispensingSize(name=name)
        with SaveContextManager(dispensing_size, model=DispensingSize):
            message = [SUCCESS_RESPONSES[
                       "creation_success"].format("Dispensing Size")]
            return CreateDispensingSize(
                message=message, dispensing_size=dispensing_size)


class EditDispensingSize(graphene.Mutation):
    """
    update dispensing size
    """
    dispensing_size = graphene.Field(DispensingSizeType)
    message = graphene.String()

    class Arguments:
        name = graphene.String()
        id = graphene.Int()

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError(PRODUCTS_ERROR_RESPONSES["invalid_input_error"])
        dispensing_size = get_model_object(DispensingSize, 'id', id)
        dispensing_size.name = name
        with SaveContextManager(dispensing_size, model=DispensingSize):
            message = SUCCESS_RESPONSES[
                "update_success"].format(
                "Measuremnt Unit of Id " + str(id))
            return EditDispensingSize(
                dispensing_size=dispensing_size, message=message)


class DeleteDispensingSize(graphene.Mutation):
    """
        Delete a dispensing size
    """
    dispensing_size = graphene.Field(DispensingSizeType)
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        user = info.context.user
        dispensing_size = get_model_object(DispensingSize, 'id', id)
        dispensing_size.delete(user)
        success = SUCCESS_RESPONSES[
            "deletion_success"].format(
            "Measuremnt Unit of Id " + str(id))
        return DeleteDispensingSize(success=success)
