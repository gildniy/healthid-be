import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.authentication.models import User
from healthid.apps.authentication.schema.queries.auth_queries import UserType
from healthid.apps.business.models import Business
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.business_utils.validators import ValidateBusiness
from healthid.utils.messages.business_responses import\
    BUSINESS_ERROR_RESPONSES, BUSINESS_SUCCESS_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.apps.products.models import ProductCategory
from healthid.apps.business.models import UserBusiness


class BusinesType(DjangoObjectType):
    class Meta:
        model = Business


class CreateBusiness(graphene.Mutation):
    """Creates business
    Checks whether the person creating business is super user
    if not stops person from creating business
    returns user who created the business
    """
    business = graphene.Field(BusinesType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        trading_name = graphene.String(required=True)
        legal_name = graphene.String(required=True)
        address_line_1 = graphene.String(required=True)
        address_line_2 = graphene.String()
        phone_number = graphene.String(required=True)
        business_email = graphene.String(required=True)
        city = graphene.String(required=True)
        country = graphene.String(required=True)
        local_government_area = graphene.String()
        website = graphene.String()
        facebook = graphene.String()
        twitter = graphene.String()
        instagram = graphene.String()
        logo = graphene.String()
        user = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        ValidateBusiness().validate_business(**kwargs)
        business = Business()
        for key, value in kwargs.items():
            setattr(business, key, value)
        business.user = user
        with SaveContextManager(business, model=Business) as business:
            success = [SUCCESS_RESPONSES[
                       "creation_success"].format(business.legal_name)]
            ProductCategory.objects.bulk_create(
                [ProductCategory(name="Prescription",
                                 business=business, is_default=True),
                 ProductCategory(name="OTC", business=business,
                                 is_default=True),
                 ProductCategory(name="Daily Essentials",
                                 business=business, is_default=True),
                 ProductCategory(
                     name="Beauty", business=business, is_default=True)
                 ])

            user_business = UserBusiness()
            user_business.user = user
            user_business.business = business

            user_business.save()

            return CreateBusiness(business=business, success=success)


class UpdateBusiness(graphene.Mutation):
    """
    Updates a Business by Master Admin |super user
    Arguments: trading name, legal name, number, address
    """
    business = graphene.Field(BusinesType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        id = graphene.String()
        trading_name = graphene.String()
        legal_name = graphene.String()
        address_line_1 = graphene.String()
        address_line_2 = graphene.String()
        phone_number = graphene.String()
        business_email = graphene.String()
        city = graphene.String()
        country = graphene.String()
        local_government_area = graphene.String()
        website = graphene.String()
        facebook = graphene.String()
        twitter = graphene.String()
        instagram = graphene.String()
        logo = graphene.String()
        user = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        user = info.context.user
        id = kwargs.get('id')
        business = get_model_object(Business, 'id', id)

        if business.user != user:
            update_error = BUSINESS_ERROR_RESPONSES["business_update_error"]
            raise GraphQLError(update_error)
        for(key, value) in kwargs.items():
            if key is not None:
                setattr(business, key, value)
        msg = BUSINESS_ERROR_RESPONSES["existing_business_error"]
        with SaveContextManager(business, model=Business, message=msg):
            success =\
                [SUCCESS_RESPONSES[
                    "update_success"].format(business.legal_name)]
            return UpdateBusiness(business=business, success=success)


class AddUserBusiness(graphene.Mutation):
    class Arguments:
        user_id = graphene.String(required=True)
        business_id = graphene.String(required=True)

    user = graphene.Field(UserType)
    errors = graphene.List(graphene.String)
    message = graphene.List(graphene.String)

    @staticmethod
    @login_required
    @user_permission()
    def mutate(root, info, **kwargs):
        user_id = kwargs.get('user_id')
        business_id = kwargs.get('business_id')
        user_instance = get_model_object(User, 'id', user_id)
        business_instance = get_model_object(Business, 'id', business_id)
        business_instance.user = user_instance
        user_instance.save()
        message = [
            BUSINESS_SUCCESS_RESPONSES[
                "add_user_to_business_success"
            ].format(user_instance.email,
                     business_instance.legal_name)
        ]
        return AddUserBusiness(user=user_instance, message=message)


class DeleteBusiness(graphene.Mutation):
    """Deletes a Business
    This also perform the delete action after validating user
    """
    business = graphene.Field(BusinesType)
    success = graphene.List(graphene.String)
    error = graphene.List(graphene.String)

    class Arguments:
        id = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, id):
        user = info.context.user
        business = get_model_object(Business, 'id', id)
        business.delete(user)
        success = [SUCCESS_RESPONSES["deletion_success"].format("Business")]

        return DeleteBusiness(success=success)


class Mutation(graphene.ObjectType):
    create_business = CreateBusiness.Field()
    delete_business = DeleteBusiness.Field()
    update_business = UpdateBusiness.Field()
    add_user_business = AddUserBusiness.Field()
