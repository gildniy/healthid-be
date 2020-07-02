import graphene
import json
import copy
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required
from django.core import serializers
from django.forms import model_to_dict

from healthid.apps.orders.models import Suppliers, SupplierRevisions
from healthid.apps.orders.models import SuppliersContacts as SuppliersContactsModel
from healthid.apps.orders.models import SuppliersMeta as SuppliersMetaModel
from healthid.utils.app_utils.validator import validator
from healthid.apps.orders.schema.suppliers_query import SuppliersType, SupplierRevisionType
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)
from healthid.utils.messages.orders_responses import \
    ORDERS_ERROR_RESPONSES, ORDERS_SUCCESS_RESPONSES
from healthid.apps.orders.schema.mutations.suppliers.edit_supplier_contacts \
    import EditSupplierContacts
from healthid.apps.orders.schema.mutations.suppliers.edit_supplier_meta \
    import EditSupplierMeta
from healthid.utils.app_utils.get_user_business import get_user_business
from healthid.apps.outlets.models import Outlet, Country, City


class SuppliersContacts(graphene.InputObjectType):
    email = graphene.String()
    mobile_number = graphene.String()
    address_line_1 = graphene.String()
    address_line_2 = graphene.String()
    lga = graphene.String()
    city_id = graphene.Int()
    country_id = graphene.Int()
    outlet_id = graphene.Int()


class SuppliersMeta(graphene.InputObjectType):
    display_name = graphene.String()
    credit_days = graphene.Int()
    logo = graphene.String()
    payment_terms = graphene.String(required=True)
    commentary = graphene.String()


class EditSupplier(graphene.Mutation):
    """
    Edit a supplier's details

    args:
        id(str): id of the supplier to be edited
        name(str): name of the supplier
        email(str): contact email
        mobile_number(str): contact number
        address_line_1(str): address line 1
        address_line_2(str): address line 2
        lga(str): lga/region name
        city_id(int): id of the city
        tier_id(int): id of the tier
        country_id(int): id of the country
        credit_days(int): credit_days
        logo(str): logo
        payment_terms(str): payment_terms
        commentary(str): commentary

    returns:
        edit_request(obj): 'Suppliers' model object detailing the edit request
        message(str): success message confirming supplier edit
    """

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        tier_id = graphene.Int()
        contacts = SuppliersContacts()
        meta = SuppliersMeta()

    edit_request = graphene.Field(SupplierRevisionType)
    message = graphene.Field(graphene.String)

    @classmethod
    def validate_fields(cls, info, supplier, kwargs):
        fields = kwargs.copy()
        if fields.get('name'):
            fields['name'] = fields['name'].strip()
            fields['name'] = validator.special_character_validation(
                fields.get('name'), 'supplier name')
        
        if not fields.get('tier_id'):
            fields['tier_id'] = supplier.tier_id

        del fields['id']
        return fields

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')
        contacts = kwargs.get('contacts') or None
        meta = kwargs.get('meta') or None
        supplier = get_model_object(Suppliers, 'id', id)
        supplier_contacts_items = supplier.get_supplier_contacts
        supplier_meta = get_model_object(SuppliersMetaModel, 'supplier', supplier)

        if not supplier.is_approved:
            msg = ORDERS_ERROR_RESPONSES[
                "supplier_edit_proposal_validation_error"]
            raise GraphQLError(msg)

        logged_in_business_id = get_user_business(info.context.user).id
        supplier_business_id = supplier.business.all()[0].id

        if logged_in_business_id != supplier_business_id:
            msg = ORDERS_ERROR_RESPONSES[
                "not_allowed_to_edit_this_supplier"]
            raise GraphQLError(msg)

        fields = cls.validate_fields(info, supplier, kwargs)
        keys = ["name", "tier_id"]
        new_supplier = copy.copy(supplier)
        for key in keys:
            if key in fields:
                new_supplier.__dict__[key] = fields[key]

        supplier_contacts_model = SuppliersContactsModel()
        supplier_contacts = [
            contact for contact in supplier_contacts_items 
            if contact['outlet_id'] == contacts['outlet_id']
        ][0]

        if contacts:
            for key in supplier_contacts.keys():
                supplier_contacts_model.city = get_model_object(City, 'id', supplier_contacts["city_id"])
                supplier_contacts_model.country = get_model_object(Country, 'id', supplier_contacts["country_id"])
                supplier_contacts_model.outlet = get_model_object(Outlet, 'id', supplier_contacts['outlet_id'])

                if key in contacts:
                    supplier_contacts_model.__dict__[key] = supplier_contacts[key] 

        if contacts:
            for key in supplier_contacts_model.__dict__:
                if key in contacts:
                    supplier_contacts_model.__dict__[key] = contacts[key]

            if "city_id" in contacts:
                supplier_contacts_model.city = get_model_object(City, 'id', contacts["city_id"])
            if "country_id" in contacts:
                supplier_contacts_model.country = get_model_object(Country, 'id', contacts["country_id"])

        if meta:
            for key in supplier_meta.__dict__:
                if key in meta:
                    supplier_meta.__dict__[key] = meta[key]

        if model_to_dict(supplier) == model_to_dict(new_supplier) \
            and not contacts and not meta:
            raise GraphQLError("No new information")

        revision = serializers.serialize(
                "json",
                [
                    new_supplier,
                    supplier_contacts_model,
                    supplier_meta
                ])

        msg = ORDERS_SUCCESS_RESPONSES[
                "supplier_edit_request_success"].format(supplier.name)
        edit_request = SupplierRevisions(
            supplier=supplier,
            proposed_by=info.context.user,
            version=revision)
        edit_request.save()
        edit_request.version = json.loads(edit_request.version)

        return cls(edit_request, msg)
