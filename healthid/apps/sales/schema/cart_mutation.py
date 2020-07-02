import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.apps.sales.schema.cart_query import CartItemType
from healthid.apps.sales.models import Cart, CartItem
from healthid.apps.products.models import Product
from healthid.utils.messages.sales_responses import\
    SALES_SUCCESS_RESPONSES, SALES_ERROR_RESPONSES


class AddCartItem(graphene.Mutation):
    '''
    Adds a product along with quantity to cart.

    args:
        product_id: id of product you want to add to cart.
        quantity: amount of the product to add to cart.

    returns:
        success: message to signal that a product has been added to cart
        cart_item: the product that has been added to cart alon with the
                   quantity
    '''
    class Arguments:
        product_id = graphene.Int(required=True)
        quantity = graphene.Int(required=True)

    success = graphene.String()
    cart_item = graphene.Field(CartItemType)

    @login_required
    def mutate(self, info, **kwargs):
        quantity = kwargs.get('quantity')
        product_id = kwargs.get('product_id')

        cart, _ = Cart.objects.get_or_create(user=info.context.user)
        product = get_model_object(Product, 'id', product_id)
        if not product.is_approved:
            raise GraphQLError(
                SALES_ERROR_RESPONSES[
                    "unapproved_product_error"].format(product.product_name))
        if quantity > product.quantity_in_stock:
            raise GraphQLError(
                SALES_ERROR_RESPONSES[
                    "in_stock_product_error"].format(
                        product.quantity_in_stock, product.product_name))
        cart_item = CartItem(product=product, quantity=quantity)
        with SaveContextManager(cart_item) as cart_item:
            cart.items.add(cart_item)
            return AddCartItem(success=SALES_SUCCESS_RESPONSES[
                               "add_to_cart_success"],
                               cart_item=cart_item)


class Mutation(graphene.ObjectType):
    add_to_cart = AddCartItem.Field()
