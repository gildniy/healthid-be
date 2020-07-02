import graphene
from django.db.models import Q
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.outlets.models import \
    City, Country, Outlet, OutletKind, OutletMeta, OutletContacts
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES
from healthid.apps.authentication.schema.queries.auth_queries import UserType


class OutletType(DjangoObjectType):
    active_outlet_users = graphene.List(UserType)
    date_launched = graphene.String()
    address_line1 = graphene.String()
    address_line2 = graphene.String()
    lga = graphene.String()
    phone_number = graphene.String()
    prefix_id = graphene.String()
    tax_number = graphene.String()

    class Meta:
        model = Outlet

    def resolve_active_outlet_users(self, info, **kwargs):
        """
        get's users active in an outlet

        Returns:
            list(obj): users who are active in an outlet
        """
        return self.active_outlet_users


class CityType(DjangoObjectType):
    class Meta:
        model = City


class CountryType(DjangoObjectType):
    class Meta:
        model = Country


class OutletKindType(DjangoObjectType):
    class Meta:
        model = OutletKind


class OutletMetaType(DjangoObjectType):
    class Meta:
        model = OutletMeta


class OutletContactsType(DjangoObjectType):
    class Meta:
        model = OutletContacts


class OutletQuery(graphene.ObjectType):
    """
    Return a list of outlets.
    Or return a single outlet specified.
    """
    errors = graphene.Field(graphene.String)
    outlets = graphene.List(OutletType)
    outlets_meta = graphene.List(OutletMetaType)
    outlets_contact = graphene.List(OutletContactsType)
    outlet = graphene.Field(
        OutletType,
        id=graphene.Int(),
        name=graphene.String(),
        kind_id=graphene.Int()
    )

    @login_required
    def resolve_outlets(self, info, **kwargs):
        outlets = Outlet.objects.all()
        outlets_meta = OutletMeta.objects.all()
        outlets_contact = OutletContacts.objects.all()
        for outlet in outlets:
            for outlet_meta in outlets_meta:
                if outlet.id == outlet_meta.__dict__['outlet_id']:
                    outlet.__dict__[outlet_meta.__dict__['dataKey']] = \
                        outlet_meta.__dict__['dataValue']
                else:
                    outlet.__dict__[outlet_meta.__dict__['dataKey']] = None
            for outlet_contact in outlets_contact:
                if outlet.id == outlet_contact.__dict__['outlet_id']:
                    outlet.__dict__[outlet_contact.__dict__[
                        'dataKey']] = outlet_contact.__dict__['dataValue']
                else:
                    outlet.__dict__[outlet_contact.__dict__['dataKey']] = None
        return outlets

    @login_required
    def resolve_outlet(self, info, **kwargs):
        id = kwargs.get('id')
        outlets_meta = OutletMeta.objects.all()
        outlets_contact = OutletContacts.objects.all()
        if id is not None:
            outlet = get_model_object(Outlet, 'id', id)
            for outlet_meta in outlets_meta:
                if id == outlet_meta.__dict__['outlet_id']:
                    outlet.__dict__[outlet_meta.__dict__[
                        'dataKey']] = outlet_meta.__dict__['dataValue']
                else:
                    outlet.__dict__[outlet_meta.__dict__['dataKey']] = None
            for outlet_contact in outlets_contact:
                if id == outlet_contact.__dict__['outlet_id']:
                    outlet.__dict__[outlet_contact.__dict__[
                        'dataKey']] = outlet_contact.__dict__['dataValue']
                else:
                    outlet.__dict__[outlet_contact.__dict__['dataKey']] = None
            return outlet

        return None

    @login_required
    def resolve_outlets_meta(self, info, **kwargs):
        return OutletMeta.objects.all()

    @login_required
    def resolve_outlets_contact(self, info, **kwargs):
        return OutletContacts.objects.all()


class CityQuery(graphene.ObjectType):
    errors = graphene.Field(graphene.String)
    cities = graphene.List(CityType)
    city = graphene.Field(
        CityType,
        id=graphene.Int(),
        name=graphene.String(),
    )

    @login_required
    def resolve_cities(self, info, **kwargs):
        return City.objects.all()

    @login_required
    def resolve_city(self, info, **kwargs):
        city_id = kwargs.get('id')
        city_name = kwargs.get('name', ' ').title()
        if (city_id or city_name) is not None:
            city = City.objects.filter(
                Q(id=city_id) | Q(name=city_name)
            ).first()
            if city is None:
                raise GraphQLError(
                    OUTLET_ERROR_RESPONSES["inexistent_city_error"])
            return city
        raise GraphQLError(
            OUTLET_ERROR_RESPONSES["city_query_invalid_input_error"])


class CountryQuery(graphene.ObjectType):
    errors = graphene.Field(graphene.String)
    countries = graphene.List(CountryType)
    country = graphene.Field(
        CountryType,
        id=graphene.Int(),
        name=graphene.String()
    )

    @login_required
    def resolve_countries(self, info, **kwargs):
        return Country.objects.all()

    @login_required
    def resolve_country(self, info, **kwargs):
        ctry_id = kwargs.get('id')
        ctry_name = kwargs.get('name', '').title()
        if (ctry_id or ctry_name) is not None:
            ctry = Country.objects.filter(
                Q(id=ctry_id) | Q(name=ctry_name)
            ).first()
            if ctry is None:
                raise GraphQLError(
                    OUTLET_ERROR_RESPONSES["inexistent_country_error"])
            return ctry
        raise GraphQLError(
            OUTLET_ERROR_RESPONSES["city_query_invalid_input_error"])


class Query(
    OutletQuery,
    CityQuery,
    CountryQuery,
    graphene.ObjectType
):
    pass
