import json
from collections import namedtuple

import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.preference.models import (Currency, Timezone, Vat,
                                             OutletPreference)
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission


class TimezoneType(DjangoObjectType):
    class Meta:
        model = Timezone


class PreferenceType(DjangoObjectType):
    class Meta:
        model = OutletPreference


class VatType(DjangoObjectType):
    class Meta:
        model = Vat


def _json_object_hook(d):
    # Converting JSON to Python objects
    return namedtuple('X', d.keys())(*d.values())


def json_to_obj(data):
    return json.loads(data, object_hook=_json_object_hook)


class RawCurrency(graphene.ObjectType):
    # Structures the JSON output returned in GraphQL
    name = graphene.String()
    symbol = graphene.String()
    symbol_native = graphene.String()
    decimal_digits = graphene.Int()
    rounding = graphene.Int()
    code = graphene.String()
    name_plural = graphene.String()
    business_id = graphene.String()


class CurrencyType(DjangoObjectType):
    class Meta:
        model = Currency


class Query(graphene.ObjectType):
    """
    Return all time zones.
    Return a list of currencies or return a single curency specified.
    """
    timezones = graphene.List(TimezoneType)
    outlet_preference = graphene.Field(PreferenceType,
                                       outlet_id=graphene.Int())

    currencies = graphene.List(RawCurrency)
    currency = graphene.Field(
        CurrencyType,
        id=graphene.String(),
        name=graphene.String(),
        symbol=graphene.String(),
        symbol_native=graphene.String(),
        decimal_digits=graphene.Int(),
        rounding=graphene.Int(),
        code=graphene.String(),
        name_plural=graphene.String(),
        business_id=graphene.String()
    )

    vat = graphene.Field(
        VatType,
        id=graphene.String()
    )
    success = graphene.List(graphene.String)

    @login_required
    @user_permission()
    def resolve_timezones(self, info, **kwargs):
        return Timezone.objects.all()

    @login_required
    def resolve_outlet_preference(self, info, **kwargs):
        id = kwargs.get('outlet_id')
        return get_model_object(OutletPreference, 'outlet_id', id)

    @login_required
    def resolve_currencies(self, args):
        # returns all currencies from the fixture file
        currencies = Currency.get_currency_formats()
        return json_to_obj(json.dumps(currencies))

    @login_required
    def resolve_currency(self, info, **kwargs):
        # returns currency from db by currency name
        name = kwargs.get('name')

        if name is not None:
            return get_model_object(Currency, 'name', name)
        return None

    @login_required
    def resolve_vat(self, info, **kwargs):
        # returns vat from db by id
        id = kwargs.get('id')
        return get_model_object(Vat, 'id', id)
