import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.sales.models import CartItem, Cart


class CartItemType(DjangoObjectType):
    class Meta:
        model = CartItem


class CartType(DjangoObjectType):
    total = graphene.Float()

    class Meta:
        model = Cart

    def resolve_total(self, info, **kwargs):
        return self.total


class Query(graphene.AbstractType):
    cart = graphene.Field(CartType)

    @login_required
    def resolve_cart(self, info, **kwargs):
        '''
        Method that returns a cart of a logged in user.
        '''
        cart, _ = Cart.objects.get_or_create(user=info.context.user)
        return cart
