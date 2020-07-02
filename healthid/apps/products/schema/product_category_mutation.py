import graphene
from django.forms import model_to_dict
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import ProductCategory
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES
from .product_query import ProductCategoryType
from healthid.apps.products.models import Product
from healthid.utils.app_utils.get_user_business import get_user_business


class CreateProductCategory(graphene.Mutation):
    """
        Mutation to create a Product Category
    """
    product_category = graphene.Field(ProductCategoryType)

    class Arguments:
        name = graphene.String(required=True)
        business_id = graphene.String()
        loyalty_weight = graphene.Int()
        amount_paid = graphene.Int()
        markup = graphene.Int(required=True)
        is_vat_applicable = graphene.Boolean(required=True)

    message = graphene.String()

    @login_required
    @user_permission('Master Admin')
    def mutate(self, info, **kwargs):
        business = get_user_business(info.context.user)
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError(PRODUCTS_ERROR_RESPONSES["invalid_input_error"])
        kwargs["business_id"] = business.id
        params = {'model': ProductCategory,
                  'field': 'name', 'value': kwargs.get('name')}
        product_category = ProductCategory(**kwargs)
        with SaveContextManager(product_category, **params):
            message = SUCCESS_RESPONSES[
                "creation_success"].format("Product Category")
            return CreateProductCategory(
                message=message, product_category=product_category)


class EditProductCategory(graphene.Mutation):
    """
    Mutation to edit a Product Category
    """
    product_category = graphene.Field(ProductCategoryType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        loyalty_weight = graphene.Int()
        amount_paid = graphene.Int()
        markup = graphene.Int()
        is_vat_applicable = graphene.Boolean()

    @login_required
    @user_permission('Master Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        name = kwargs.get('name')
        if name.strip() == "":
            raise GraphQLError(PRODUCTS_ERROR_RESPONSES["invalid_input_error"])
        product_category = get_model_object(ProductCategory, 'id', id)

        changed_fields = {
            key: kwargs.get(key)
            for key, value in model_to_dict(product_category).items()
            if key in kwargs and value != kwargs.get(key)}

        if not changed_fields:
            return EditProductCategory(
                message=PRODUCTS_ERROR_RESPONSES["product_category_no_edits"],
                product_category=product_category)

        products = Product.objects.filter(product_category_id=id)

        if len(products):
            for product in products:
                for field, value in changed_fields.items():
                    if field != 'name':
                        setattr(product, field, value)
                        if field == 'is_vat_applicable':
                            product.vat_status = value
                        product.save()

        for field, value in changed_fields.items():
            setattr(product_category, field, value)

        with SaveContextManager(product_category, model=ProductCategory):
            message = SUCCESS_RESPONSES[
                "update_success"].format("Product Category")
            return EditProductCategory(
                message=message,
                product_category=product_category)


class DeleteProductCategory(graphene.Mutation):
    """
        Delete a product category
    """
    product_category = graphene.Field(ProductCategoryType)
    message = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission('Master Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        user = info.context.user
        product_category = get_model_object(ProductCategory, 'id', id)
        if product_category.is_default:
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["default_product_category_error"])
        product_category.delete(user)
        message = SUCCESS_RESPONSES[
            "deletion_success"].format(
            "Product category of Id " + str(id))

        return DeleteProductCategory(message=message)
