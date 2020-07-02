from datetime import datetime

import graphene
from dateutil.relativedelta import relativedelta
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.products.schema.product_query import (
    Product
)
from healthid.apps.sales.models import (
    Promotion, PromotionType as PromotionTypeModel
)
from healthid.apps.outlets.models import Outlet
from healthid.apps.sales.schema.promotions_query import (
    PromotionType, PromotionTypeModelType
)
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_is_active_in_outlet
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.sales_responses import \
    SALES_ERROR_RESPONSES, SALES_SUCCESS_RESPONSES
from healthid.utils.sales_utils.validators import (
    validate_fields, add_products_to_promotion,
    set_recommended_promotion
)


class CreatePromotionType(graphene.Mutation):
    """
    Create a new promotion type

    args:
        name(str): name of the promotion type to be created

    returns:
        success(str): success message confirming promotion type creation
        promotion_type(obj): 'PromotionType' object containing details of
                             the newly created promotion type.
    """

    class Arguments:
        name = graphene.String(required=True)

    success = graphene.String()
    promotion_type = graphene.Field(PromotionTypeModelType)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError(SALES_ERROR_RESPONSES["promotion_type_error"])
        params = {'model': PromotionTypeModel}
        promotion_type = PromotionTypeModel(name=name)
        with SaveContextManager(promotion_type, **params) as promotion_type:
            success = SUCCESS_RESPONSES[
                "creation_success"].format("Promotion Type")
            return CreatePromotionType(
                success=success, promotion_type=promotion_type)


class CreatePromotion(graphene.Mutation):
    """
    Create a new promotion for an outlet.

    args:
        title(str): Title of the promotion you to be created
        promotion_type_id(str): id of the related promotion type that the
                                promotion will fall under
        description(str): description of the promotion to be created
        product_ids(list): list of ids for the products that the promotion will
                           be applied to
        discount(float): the value of the discount for the promotion
        outlet_id(int): the id of the outlets that will apply the promotion
                        and discounts

    returns:
        success(str): success message confirming promotion creation
        promotion(obj): 'Promotion' object containing details of
                        the newly created promotion.
    """

    class Arguments:
        title = graphene.String(required=True)
        promotion_type_id = graphene.String(required=True)
        description = graphene.String(required=True)
        product_ids = graphene.List(graphene.Int)
        discount = graphene.Float(required=True)
        outlet_id = graphene.Int(required=True)

    success = graphene.String()
    promotion = graphene.Field(PromotionType)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        promotion = validate_fields(Promotion(), **kwargs)
        outlet_id = kwargs.get('outlet_id')
        user = info.context.user
        check_user_is_active_in_outlet(user, outlet_id=outlet_id)
        with SaveContextManager(promotion, model=Promotion) as promotion:
            product_ids = kwargs.get('product_ids', [])
            promotion = add_products_to_promotion(promotion, product_ids)
            return CreatePromotion(
                success=SUCCESS_RESPONSES[
                    "creation_success"].format("Promotion"),
                promotion=promotion)


class CreateRecommendedPromotion(graphene.Mutation):
    """
    Create a recommended promotion for an outlet.

    args:
        outlet_id(int): the id of the outlets that will apply the promotion
                        and discounts

    returns:
        success(str): success message confirming promotion creation
        promotion(obj): 'Promotion' object containing details of
                        the newly created promotion.
    """

    class Arguments:
        outlet_id = graphene.Int(required=True)

    success = graphene.String()

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        outlet_id = kwargs.get('outlet_id')
        user = info.context.user
        check_user_is_active_in_outlet(user, outlet_id=outlet_id)
        today_date = datetime.now()
        twelve_month = today_date + relativedelta(months=+12)
        outlet = get_model_object(Outlet, 'id', outlet_id)
        near_expired_products = Product.objects \
            .for_business(outlet.business.id) \
            .filter(nearest_expiry_date__range=(today_date, twelve_month))
        promotion_set = set_recommended_promotion(Promotion,
                                                  near_expired_products)
        return CreateRecommendedPromotion(
            success='Promotion set on {} product(s)'.format(promotion_set))


class UpdatePromotion(graphene.Mutation):
    """
    Create a new promotion for an outlet.

    args:
        title(str): title of the promotion to be created
        promotion_type_id(str): id of the related promotion type that the
                                promotion will fall under
        description(str): description of the promotion to be created
        product_ids(list): list of ids for the products that the promotion will
                           be applied to
        discount(float): the value of the discount for the promotion
        outlet_id(int): the id of the outlets that will apply the promotion
                        and discounts

    returns:
        success(str): success message confirming promotion update
        promotion(obj): 'Promotion' object containing details of
                        the newly created promotion.
    """

    class Arguments:
        promotion_id = graphene.String(required=True)
        title = graphene.String()
        promotion_type_id = graphene.String()
        description = graphene.String()
        product_ids = graphene.List(graphene.Int)
        discount = graphene.Float()

    success = graphene.String()
    promotion = graphene.Field(PromotionType)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        promotion_id = kwargs.pop('promotion_id')
        user = info.context.user
        promotion = get_model_object(Promotion, 'id', promotion_id)
        check_user_is_active_in_outlet(user, outlet=promotion.outlet)
        product_ids = \
            kwargs.pop('product_ids') if kwargs.get('product_ids') else []
        validate_fields(Promotion(), **kwargs)
        for (key, value) in kwargs.items():
            setattr(promotion, key, value)
        with SaveContextManager(promotion, model=Promotion) as promotion:
            promotion = add_products_to_promotion(promotion, product_ids)
            return UpdatePromotion(success=SUCCESS_RESPONSES[
                "update_success"].format("Promotion"),
                promotion=promotion)


class DeletePromotion(graphene.Mutation):
    """
    Delete a promotion for an outlet.

    args:
        promotion_id(str): id of the promotion to be deleted

    returns:
        success(str): success message confirming promotion deletion
        promotion(obj): 'Promotion' object containing details of
                        the newly deleted promotion.
    """

    class Arguments:
        promotion_id = graphene.String(required=True)

    success = graphene.String()

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        promotion_id = kwargs.get('promotion_id')
        user = info.context.user
        promotion = get_model_object(Promotion, 'id', promotion_id)
        check_user_is_active_in_outlet(user, outlet=promotion.outlet)
        promotion.delete(user)
        return DeletePromotion(
            success=SUCCESS_RESPONSES[
                "deletion_success"].format("Promotion"))


class ApprovePromotion(graphene.Mutation):
    """
    Approve a promotion for an outlet.

    args:
        promotion_id(str): id of the promotion to be deleted

    returns:
        success(str): success message confirming promotion approval
        promotion(obj): 'Promotion' object containing details of
                        the newly approved promotion.
    """

    class Arguments:
        promotion_id = graphene.String(required=True)

    success = graphene.String()
    promotion = graphene.Field(PromotionType)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        promotion_id = kwargs.get('promotion_id')
        user = info.context.user
        promotion = get_model_object(Promotion, 'id', promotion_id)
        check_user_is_active_in_outlet(user, outlet=promotion.outlet)
        promotion.is_approved = True
        promotion.save()
        return ApprovePromotion(
            success=SALES_SUCCESS_RESPONSES["promotion_approval_success"],
            promotion=promotion)


class Mutation(graphene.ObjectType):
    create_promotion = CreatePromotion.Field()
    update_promotion = UpdatePromotion.Field()
    delete_promotion = DeletePromotion.Field()
    create_promotion_type = CreatePromotionType.Field()
    approve_promotion = ApprovePromotion.Field()
    create_recommended_promotion = CreateRecommendedPromotion.Field()
