import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.business.models import Business
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission


class BusinessType(DjangoObjectType):
    class Meta:
        model = Business


class Query(graphene.ObjectType):
    """
    Returns details of all businesses in the 'Business' model,
    or returns all the details for a specific business

    Args:
        id(string) @property: id of the business whose details are to be queried

    Returns:
        list of 'Business' objects: when querying 'businesses'
        single 'Business' object" when querying 'busniess'
    """

    businesses = graphene.List(BusinessType)
    business = graphene.Field(
        BusinessType,
        id=graphene.String(),
        trading_name=graphene.String(),
        legal_name=graphene.String(),
        primary_address=graphene.String(),
        primary_phone_number=graphene.String(),
        email=graphene.String(),
        website=graphene.String(),
        facebook=graphene.String(),
        twitter=graphene.String(),
        instagram=graphene.String(),
        logo=graphene.String(),
        date_created=graphene.String(),
        user=graphene.String()
    )

    @login_required
    @user_permission()
    def resolve_businesses(self, info, **kwargs):
        return Business.objects.all()

    @login_required
    def resolve_business(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return get_model_object(Business, 'id', id)
        return None
