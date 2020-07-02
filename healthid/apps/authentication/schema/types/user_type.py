import graphene
from graphene_django import DjangoObjectType
from healthid.utils.app_utils.database import get_model_object

from healthid.apps.authentication.models import User
from healthid.apps.outlets.models import Outlet
from healthid.utils.auth_utils.user_outlet_metadata import merge_metadata_to_user_outlet_object


class ActiveOutletType(DjangoObjectType):
    address_line1 = graphene.String()
    phone_number = graphene.String()
    date_launched = graphene.String()
    address_line2 = graphene.String()
    lga = graphene.String()
    prefix_id = graphene.String()

    class Meta:
        model = Outlet


class UserType(DjangoObjectType):
    active_outlet = graphene.Field(ActiveOutletType)
    active_outlets = graphene.List(ActiveOutletType)

    class Meta:
        model = User
        exclude_fields = ['password']

    def resolve_active_outlet(self, info, **kwargs):
        """
        get's outlet a user is active in

        Returns:
            obj: outlet user is active in
        """
        if not self.active_outlet:
            return None
        return merge_metadata_to_user_outlet_object(self.active_outlet.id)

    def resolve_active_outlets(self, info, **kwargs):
        """
        get's outlets a user is active in

        Returns:
            objs: outlets user is active in
        """
        active_outlets = self.active_outlets
        if not active_outlets:
            return None
        return active_outlets
