import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required
from django.core import serializers

from healthid.apps.orders.schema.suppliers_query import (
    SuppliersType)
from healthid.apps.orders.models import Suppliers, SupplierRevisions
from healthid.utils.app_utils.get_user_business import (
    get_user_business
)
from healthid.utils.app_utils.database import (SaveContextManager)
from healthid.utils.app_utils.validator import validator
from healthid.apps.orders.schema.mutations.suppliers.add_supplier_contacts \
    import AddSupplierContacts
from healthid.apps.orders.schema.mutations.suppliers.add_supplier_meta \
    import AddSupplierMeta
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.apps.outlets.models import Outlet


class SuppliersInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    tier_id = graphene.Int()


class SuppliersInputContacts(graphene.InputObjectType):
    email = graphene.String()
    mobile_number = graphene.String()
    address_line_1 = graphene.String()
    address_line_2 = graphene.String()
    lga = graphene.String()
    city_id = graphene.Int()
    country_id = graphene.Int()
    outlet_id = graphene.Int(required=True)


class SuppliersInputMeta(graphene.InputObjectType):
    display_name = graphene.String()
    credit_days = graphene.Int()
    logo = graphene.String()
    payment_terms = graphene.String(required=True)
    commentary = graphene.String()


class AddSupplier(graphene.Mutation):
    """
    Add a new supplier to the database

    args:
        on_duplicate(str): action to perform when the
                          supplier with the same name already exists
                          To add the supplier as new it should have
                          'NEW' as value
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
        supplier(obj): 'Suppliers' model object detailing the created supplier.
    """

    class Arguments:
        input = SuppliersInput(required=True)
        contacts_input = SuppliersInputContacts()
        meta_input = SuppliersInputMeta()

    supplier = graphene.Field(SuppliersType)

    @classmethod
    def validate_fields(cls, input, user):
        fields = input
        fields['name'] = input['name'].strip()
        fields['name'] = validator.special_character_validation(
            input['name'], 'supplier name')
        supplier = Suppliers.objects.filter(name__iexact=fields['name'].strip())
        businesses = []
        for one_supplier in supplier:
            businesses.append(one_supplier.business.first())
        if get_user_business(user) in businesses:
            raise GraphQLError(
                ERROR_RESPONSES['duplication_error'].format(fields['name']))
        fields['supplier'] = supplier
        return fields

    @classmethod
    @login_required
    def mutate(cls, root, info, input=None,
               contacts_input=None, meta_input=None):
        user = info.context.user
        supplier = Suppliers()

        business = get_user_business(user)
        fields = cls.validate_fields(input, user)

        # contacts input
        contacts_fields = AddSupplierContacts.validate_fields(
            contacts_input) if contacts_input else None
        # meta input
        meta_fields = AddSupplierMeta.validate_fields(
            meta_input) if meta_input else None

        for (key, value) in fields.items():
            setattr(supplier, key, value)

        supplier.user = user

        current_outlet = contacts_fields['outlet_id']
        with SaveContextManager(supplier, model=Suppliers) as supplier:
            data = supplier
            supplier_contact_items = []
            if contacts_fields:
                contacts_fields['supplier_id'] = supplier.id

                supplier_contact_items = AddSupplierContacts.mutate(
                    root, info, contacts_fields)
    
                business_outlets = Outlet.objects.filter(business_id=business.id)
                for outlet in business_outlets:
                    if current_outlet == outlet.id:
                        continue
                    contacts_fields['outlet_id'] = outlet.id
                    contacts_fields['supplier_id'] = supplier.id
                    AddSupplierContacts.mutate(root, info, contacts_fields)

            if meta_fields:
                meta_fields['supplier_id'] = supplier.id
                meta_fields['display_name'] = meta_fields.get('display_name') \
                    or f'{supplier.name} ({supplier.supplier_id})'
                try:
                    supplier_meta = AddSupplierMeta.mutate(
                        root, info, meta_fields)
                    data.supplier_meta = supplier_meta
                    supplier.business.add(business)
                    data.supplier_contacts = supplier.get_supplier_contacts
                except Exception as error:
                    for supplier_contact in supplier_contact_items:
                        supplier_contact.hard_delete()
                        supplier.hard_delete()
                        raise GraphQLError(error)

            return cls(supplier=data)
