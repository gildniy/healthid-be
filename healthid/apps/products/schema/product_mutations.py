import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.products.models import Product, ProductCategory
from healthid.apps.products.schema.batch_info_mutation import (
    ApproveProposedQuantity, CreateBatchInfo, ProposeQuantity)
from healthid.apps.products.schema.dispensing_size_mutation import (
    CreateDispensingSize, DeleteDispensingSize, EditDispensingSize)
from healthid.apps.products.schema.price_survey_mutations import (
    CreatePriceCheckSurvey, DeletePriceCheckSurvey, UpdatePriceCheckSurvey)
from healthid.apps.products.schema.product_category_mutation import (
    CreateProductCategory, DeleteProductCategory, EditProductCategory)
from healthid.apps.products.schema.product_query import (ProductCategoryType,
                                                         ProductType)
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.query_objects import GetObjectList
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.product_utils.activate_deactivate_product import \
    activate_deactivate_products
from healthid.utils.product_utils.product import set_product_attributes, addOutOfStockBatch
from healthid.utils.product_utils.product_query import ProductQuery
from healthid.utils.product_utils.set_price import SetPrice
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.products_responses import\
    PRODUCTS_ERROR_RESPONSES, PRODUCTS_SUCCESS_RESPONSES


class ProductInput(graphene.InputObjectType):
    """
        Specifying the data types of the product Input
    """
    Product = graphene.String()


class CreateEditProduct(graphene.Mutation):
    '''
    Class template for mutations that edit or create products.

    args:
        product_name(str): Name of the product to be edited
        description(str): Description of the product
        product_category_id(int): The product category id
        brand(str): The brand associated with the product
        manufacturer(str): The product manufacturer
        dispensing_size_id(int): The id of the dispensing size the product
                                  is to be served in
        preferred_supplier_id(str): The id of the preferred supplier of the
                                    product
        backup_supplier_id(str): The id of the backup supplier of the product
        vat_status(bool): toggles VAT for product
        loyalty_weight(int): The value of loyalty points the product awards
                             upon purchase
        image(str): An image URL for the product display icon
        tags(str): Description tags associated with the product
        markup(int): The markup value for the product sales price
        sku_number(int): The unique product identifier
        auto_price(bool): toogles automatic or manual settin gof the product
                          sales price.
        sales_price(int): The product sales price

    returns:
        message(str): success message confirming mutation completion
        product(obj): 'Product' object containing details of
                      the product to be edited.
    '''

    product = graphene.Field(ProductType)
    message = graphene.String()

    class Arguments:
        product_name = graphene.String(required=True)
        description = graphene.String(required=True)
        product_category_id = graphene.Int(required=True)
        brand = graphene.String(required=True)
        manufacturer = graphene.String(required=True)
        dispensing_size_id = graphene.Int(required=True)
        preferred_supplier_id = graphene.String()
        backup_supplier_id = graphene.String()
        vat_status = graphene.Boolean(required=True)
        loyalty_weight = graphene.Int(required=True)
        image = graphene.String()
        tags = graphene.List(graphene.String)
        markup = graphene.Int()
        sku_number = graphene.Int()
        auto_price = graphene.Boolean()
        sales_price = graphene.Int()
        global_upc = graphene.String()
        reorder_point = graphene.Int()
        reorder_max = graphene.Int()

    def mutate(self, info, **kwargs):
        pass


class CreateProduct(CreateEditProduct):
    """
    Mutation to create a product. Inherits from the
    'CreateEditProduct' class.
    """
    @login_required
    def mutate(self, info, **kwargs):
        product_category_id = kwargs.pop('product_category_id')

        product_category = get_model_object(
            ProductCategory, 'id', product_category_id)
        product = Product(business=product_category.business,
                          product_category=product_category,
                          markup=product_category.markup)
        output = set_product_attributes(product, **kwargs)
        message = 'Product successfully created'

        return CreateProduct(product=output, message=message)


class UpdateProduct(CreateEditProduct):
    """
    Mutation to update an exitsing product. Inherits from the
    'CreateEditProduct' class.
    """
    class Arguments(CreateEditProduct.Arguments):
        id = graphene.Int(required=True)
        product_name = graphene.String()
        description = graphene.String()
        product_category_id = graphene.Int()
        brand = graphene.String()
        manufacturer = graphene.String()
        dispensing_size_id = graphene.Int()
        vat_status = graphene.Boolean()
        loyalty_weight = graphene.Int()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        id = kwargs.get('id')
        product = get_model_object(Product, 'id', id)
        roles = ("Master Admin", "Operations Admin")
        if str(user.role) in roles and product.is_approved:
            output = set_product_attributes(product, **kwargs)
            message = SUCCESS_RESPONSES["update_success"].format("Product")
            return UpdateProduct(product=output, message=message)
        if product.is_approved:
            proposed_edit = product
            proposed_edit.id = None
            output = set_product_attributes(proposed_edit, **kwargs)
            output.parent_id = kwargs.get('id')
            output.is_approved = False
            output.user = user
            output.save()
            message = PRODUCTS_SUCCESS_RESPONSES["approval_pending"]
            return UpdateProduct(product=output, message=message)
        message = PRODUCTS_ERROR_RESPONSES[
            "product_not_approved"].format(product.product_name)
        raise GraphQLError(message)


class DeleteProduct(graphene.Mutation):
    """
    Delete a single existing product from the database.

    args:
        id(int): id of the product to be deleted

    returns:
        success(str): success message confirming product deletion
        id(int): id of the newly deleted product
    """

    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    def mutate(self, info, id):
        user = info.context.user
        product = get_model_object(Product, 'id', id)
        if product.is_approved:
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["approve_deletion_error"])
        product.delete(user)

        return DeleteProduct(
            success=SUCCESS_RESPONSES["deletion_success"].format("Product"))


class ApproveProduct(graphene.Mutation):
    """
    Approve a proposed product.

    args:
        product_id(int): id of the product to be approved.

    returns:
        success(str): success message confirming product approval
        product(obj): 'Product' object containing details of
                      the newly approved product.
    """

    class Arguments:
        product_id = graphene.Int(required=True)

    product = graphene.Field(ProductType)
    success = graphene.List(graphene.String)

    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        id = kwargs.get('product_id')
        product = get_model_object(
            Product, 'id', id, manager_query=Product.all_products)
        if product.is_approved:
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES[
                    "product_approval_duplication"].format(id))
        product.is_approved = True
        product.save()
        success = [
            'message',
            SUCCESS_RESPONSES["approval_success"].format("Product " + str(id))
        ]
        addOutOfStockBatch(info.context.user, product)

        return ApproveProduct(success=success, product=product)


class ApproveProposedEdits(graphene.Mutation):
    """
    Approve a proposed edit to a product's details.

    args:
        product_id(int): id of the product whose details are to be edited
        edit_request_id(int): id of the proposed edit request

    returns:
        success(str): success message confirming edit approval
        product(obj): 'Product' object containing details of
                      the product to be edited.
    """

    class Arguments:
        product_id = graphene.Int(required=True)
        edit_request_id = graphene.Int(required=True)

    product = graphene.Field(ProductType)
    message = graphene.List(graphene.String)

    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        product_id = kwargs.get('product_id')
        request_id = kwargs.get('edit_request_id')
        message = PRODUCTS_ERROR_RESPONSES[
            "inexistent_proposed_edit"].format(request_id)

        product = get_model_object(Product, 'id', product_id)
        product.approve_proposed_edit(request_id)

        message = [SUCCESS_RESPONSES["approval_success"].format(
            "Edit request")]
        return ApproveProposedEdits(product=product, message=message)


class DeclineProposedEdits(graphene.Mutation):
    """
    Decline a proposed product detail edit. The proposed edit is NOT deleted
    when declined.

    args:
        product_id(int): id of the product whose details are
                         to be edited
        edit_request_id(int): id of the proposed edit request
        comment(str): comment detailing why the edit was declined.

    returns:
        message(str): success message confirming edit decline
        edit_request(obj): 'Product' object containing details of
        the newly approved product.
    """

    class Arguments:
        product_id = graphene.Int(required=True)
        edit_request_id = graphene.Int(required=True)
        comment = graphene.String(required=True)

    message = graphene.Field(graphene.String)
    edit_request = graphene.Field(ProductType)

    def mutate(self, info, **kwargs):
        product_id = kwargs.get('product_id')
        request_id = kwargs.get('edit_request_id')
        comment = kwargs.get('comment')

        product = get_model_object(Product, 'id', product_id)
        edit_request = product.decline_proposed_edit(request_id, comment)

        product_name = edit_request.product_name
        msg = PRODUCTS_SUCCESS_RESPONSES[
            "edit_request_decline"].format(product_name)
        return DeclineProposedEdits(message=msg, edit_request=edit_request)


class UpdatePrice(graphene.Mutation):
    """
    Update the markup, sales tax and sales price of a product.

    args:
        product_ids(list): list of ids for the products to be updated
        markup(int): markup value for the product sales price
        sales_tax(float): id of the proposed edit request
        sales_price(float): product sales price

    returns:
        message(str): success message confirming price update
        error(list): list of error messages for failed product updates
        products(list): list of updated 'Product' objects
    """

    products = graphene.List(ProductType)
    errors = graphene.List(graphene.String)
    message = graphene.String()

    class Arguments:
        markup = graphene.Int()
        sales_tax = graphene.Float()
        product_ids = graphene.List(graphene.Int)
        auto_price = graphene.Boolean()
        sales_price = graphene.Float()

    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        sales_price = kwargs.get("sales_price")
        markup = kwargs.get("markup")
        if (not markup and not sales_price) or (markup and sales_price):
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["update_price_error"])
        set_price = SetPrice()
        product_ids = kwargs.pop('product_ids')
        products = GetObjectList.get_objects(Product, product_ids)
        for product in products:
            set_price.update_product_price(product, **kwargs)
        errors = [
            error.strip('\t') for error in set_price.errors if set_price.errors
        ]
        if errors:
            return UpdatePrice(products=set_price.products, errors=errors)
        return UpdatePrice(
            products=set_price.products,
            message=PRODUCTS_SUCCESS_RESPONSES["set_price_success"].format(
                key="sales price" if sales_price else "markup",
                number=len(set_price.products),
                value=markup or sales_price)
        )


class UpdateLoyaltyWeight(graphene.Mutation):
    """
    Update the loyalty point weight for a product category.

    args:
        product_category_id(int): id of the product's relevant category
        loyalty_value(int): updated loyalty point value

    returns:
        message(str): success message confirming point update
        category(obj): 'ProductCategory' object containing the product
                       category details.
    """

    category = graphene.Field(ProductCategoryType)

    class Arguments:
        product_category_id = graphene.Int(required=True)
        loyalty_value = graphene.Int(required=True)

    message = graphene.String()

    @staticmethod
    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        loyalty_value = kwargs.get("loyalty_value")
        if loyalty_value < 1:
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["loyalty_weight_error"])
        product_category_id = kwargs.get("product_category_id")
        products = ProductQuery().query_product_category(product_category_id)
        category = get_model_object(ProductCategory, 'id', product_category_id)
        for product in products:
            product.loyalty_weight = loyalty_value
            product.save()

        message = SUCCESS_RESPONSES["update_success"].format("Loyalty weight")
        return UpdateLoyaltyWeight(category=category, message=message)


class UpdateAProductLoyaltyWeight(graphene.Mutation):
    """
    Update the loyalty point weight of a product.

    args:
    id(int): id of the product whose loyalty points are to be updated
    loyalty_value(int): updated loyalty point value

    returns:
    message(str): success message confirming loyalty point update
    product(obj): 'Product' object containing the product details
    """

    product = graphene.Field(ProductType)

    class Arguments:
        id = graphene.List(graphene.String, required=True)
        loyalty_value = graphene.Int(required=True)

    message = graphene.String()

    @staticmethod
    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        loyalty_value = kwargs.get("loyalty_value")
        product_ids = kwargs.get('id')
        if loyalty_value < 1:
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["loyalty_weight_error"])
        for product_id in product_ids:
            product = get_model_object(Product, 'id', product_id)
            product.loyalty_weight = loyalty_value
            product.save()
        message = PRODUCTS_SUCCESS_RESPONSES["loyalty_weight_updated"].format(
            len(product_ids), loyalty_value)
        return UpdateAProductLoyaltyWeight(product=product, message=message)


class ActivateDeactivateProducts(graphene.Mutation):
    """
    Class template for mutations that activate or deactivate products.

    args:
        product_ids(int): id of the product

    returns:
        message(str): success message confirming mutation completion
        products(obj): 'Product' objects containing the product details
    """

    class Arguments:
        product_ids = graphene.List(graphene.Int, required=True)

    success = graphene.String()
    products = graphene.List(ProductType)

    def mutate(self, info, **kwargs):
        pass


class ActivateProduct(ActivateDeactivateProducts):
    """
    Mutation class to activate a product. Inherits from the
    'ActivateDeactivateProducts' class.
    """

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        product_ids = kwargs.get('product_ids')
        error_msg = PRODUCTS_ERROR_RESPONSES[
            "product_activation_error"].format(product_ids)
        products = activate_deactivate_products(product_ids, False, error_msg)
        success = PRODUCTS_SUCCESS_RESPONSES[
            "product_activation_success"].format(product_ids)
        return ActivateProduct(success=success, products=products)


class DeativateProduct(ActivateDeactivateProducts):
    """
    Mutation class to deactivate a product. Inherits from the
    'ActivateDeactivateProducts' class.
    """

    @login_required
    @user_permission('Operations Admin')
    def mutate(self, info, **kwargs):
        product_ids = kwargs.get('product_ids')
        error_msg = PRODUCTS_ERROR_RESPONSES[
            "product_deactivation_error"].format(product_ids)
        products = activate_deactivate_products(product_ids, True, error_msg)
        success = PRODUCTS_SUCCESS_RESPONSES[
            "product_deactivation_success"].format(product_ids)
        return DeativateProduct(success=success, products=products)


class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()
    create_batch_info = CreateBatchInfo.Field()
    proposed_quantity = ProposeQuantity.Field()
    approve_quantity = ApproveProposedQuantity.Field()
    update_price = UpdatePrice.Field()
    approve_product = ApproveProduct.Field()
    update_loyalty_weight = UpdateLoyaltyWeight.Field()
    product_loyalty_weight_update = UpdateAProductLoyaltyWeight.Field()
    deactivate_product = DeativateProduct.Field()
    activate_product = ActivateProduct.Field()
    create_product_category = CreateProductCategory.Field()
    create_dispensing_size = CreateDispensingSize.Field()
    edit_product_category = EditProductCategory.Field()
    delete_product_category = DeleteProductCategory.Field()
    edit_dispensing_size = EditDispensingSize.Field()
    delete_dispensing_size = DeleteDispensingSize.Field()
    create_price_check_survey = CreatePriceCheckSurvey.Field()
    delete_price_check_survey = DeletePriceCheckSurvey.Field()
    update_price_check_survey = UpdatePriceCheckSurvey.Field()
    approve_proposed_edits = ApproveProposedEdits.Field()
    decline_proposed_edits = DeclineProposedEdits.Field()
