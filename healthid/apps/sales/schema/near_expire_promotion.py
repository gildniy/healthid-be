import graphene
from graphql import GraphQLError
from dateutil.relativedelta import relativedelta
from graphql_jwt.decorators import login_required

from healthid.apps.products.schema.product_query import (
    ProductType, Product
)
from healthid.apps.sales.schema.promotions_query import Promotion
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_is_active_in_outlet
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission


class CreateCustomNearExpirePromotion(graphene.Mutation):
    """
    Generate near-expiry custom discount/promotion.

    args:
        promotion_id(str): id of the promotion to be applied
        product_id(int): id of the product to be added
        apply_months(int): when the promotion will be applied

    returns:
        success(str): success message confirming promotion generated
        promotion(obj): 'Promotion' object containing details of
                        the promotion.
    """

    class Arguments:
        promotion_id = graphene.String(required=True)
        product_id = graphene.Int(required=True)
        apply_months = graphene.Int(required=True)

    success = graphene.String()
    product = graphene.Field(ProductType)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        promotion_id = kwargs.get('promotion_id')
        product_id = kwargs.get('product_id')
        apply_months = kwargs.get('apply_months')
        if apply_months < 1 or apply_months > 12:
            raise GraphQLError('Months must be between 1 and 12')
        user = info.context.user
        promotion = get_model_object(Promotion, 'id', promotion_id)
        product = get_model_object(Product, 'id', product_id)
        applied_date = product.nearest_expiry_date - relativedelta(
            months=+apply_months)
        promotion_product = promotion.products.filter(id=product_id)

        check_user_is_active_in_outlet(user, outlet=promotion.outlet)
        if not promotion_product:
            promotion.products.add(product)
        promotion.applied_date = applied_date
        promotion.save()

        return CreateCustomNearExpirePromotion(
            success='Promotion was generated successfully',
            product=product)


class Mutation(graphene.ObjectType):
    create_custom_near_expire_promotion = \
        CreateCustomNearExpirePromotion.Field()
