import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.schema.suppliers_query import (
    SupplierRatingType)
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)
from healthid.apps.orders.models import Suppliers, SupplierRating
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES


class RateSupplier(graphene.Mutation):
    """
    Rate a specific supplier after delivery

    args:
    supplier_id(str): id of the supplier to rate
    delivery_promptness(int): weither on time (1) or late (0)
    service_quality(int): from 0 to 4

    returns:
    message(str): success message confirming rating creation
    supplier_rating(obj): 'SupplierRating' model object detailing
                            the created rating
    supplier(obj): 'Suppliers' model object detailing the noted supplier
    """

    class Arguments:
        supplier_id = graphene.String(required=True)
        delivery_promptness = graphene.Int(required=True)
        service_quality = graphene.Int(required=True)

    message = graphene.Field(graphene.String)
    supplier_rating = graphene.Field(SupplierRatingType)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        supllier_id = kwargs.get("supplier_id")
        delivery_promptness = kwargs.get("delivery_promptness")
        service_quality = kwargs.get("service_quality")
        if delivery_promptness < 0 or delivery_promptness > 1:
            raise GraphQLError(ORDERS_ERROR_RESPONSES["invalid_rating"]
                               .format("delivery_promptness", 1))
        if service_quality < 0 or service_quality > 4:
            raise GraphQLError(ORDERS_ERROR_RESPONSES["invalid_rating"]
                               .format("service_quality", 4))
        supplier = get_model_object(Suppliers, "id", supllier_id)
        supplier_rating = SupplierRating(
            supplier=supplier, rating=delivery_promptness+service_quality)
        with SaveContextManager(supplier_rating,
                                model=SupplierRating) as supplier_rating:
            return cls(
                message=SUCCESS_RESPONSES[
                    "creation_success"].format("Supplier's rating"),
                supplier_rating=supplier_rating
            )
