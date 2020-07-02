import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.models import Suppliers, SuppliersContacts
from healthid.utils.app_utils.validator import validator
from healthid.apps.orders.schema.suppliers_query import \
    SuppliersType
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.orders_responses import \
    ORDERS_ERROR_RESPONSES


class EditSupplierContacts(graphene.Mutation):
    """
    Edit a supplier's details

    args:
        supplier_id(str): id of the supplier to be edited
        contact_id(str): id of the contact to be edited
        email(str): supplier contact email
        mobile_number(str): contact number
        address_line_1(str): first address line
        address_line_2(str): second address line
        lga(str): name of the supplier's local government area
        city_id(int): id of the supplier city location
        country_id(int): supplier country

    returns:
        supplier(obj): 'Suppliers' model object detailing the edited supplier
        message(str): success message confirming supplier edit
    """

    class Arguments:
        supplier_id = graphene.String(required=True)
        contact_id = graphene.String()
        email = graphene.String()
        mobile_number = graphene.String()
        address_line_1 = graphene.String()
        address_line_2 = graphene.String()
        lga = graphene.String()
        city_id = graphene.Int()
        country_id = graphene.Int()

    supplier = graphene.Field(SuppliersType)
    message = graphene.Field(graphene.String)

    @classmethod
    def validate_fields(cls, contacts, kwargs):
        fields = kwargs

        fields['supplier_id'] = kwargs.get('supplier_id')
        fields['email'] = validator.validate_email(
            fields['email']) if fields.get('email') else\
            (contacts and contacts.email) or None

        fields['mobile_number'] = validator.validate_mobile(
            fields['mobile_number']) if fields.get('mobile_number') \
            else (contacts and contacts.mobile_number) or None

        fields['address_line_1'] = fields.get(
            'address_line_1') or (contacts and contacts.address_line_1) or None

        fields['address_line_2'] = fields.get(
            'address_line_2') or (contacts and contacts.address_line_2) or None

        fields['lga'] = fields.get('lga') or (
            contacts and contacts.lga) or None
        fields['city_id'] = fields.get('city_id') or (
            contacts and contacts.city_id) or None
        fields['country_id'] = fields.get(
            'country_id') or (contacts and contacts.country_id) or None
        fields['edit_request_id'] = kwargs.get('edit_request_id')
        return fields

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):
        supplier_contacts = SuppliersContacts()
        contact_id = kwargs.get('contact_id')
        supplier_id = kwargs.get('supplier_id')
        contacts = get_model_object(SuppliersContacts, 'id', contact_id) if \
            contact_id else \
            SuppliersContacts.objects.filter(supplier_id=supplier_id).first()
        supplier = get_model_object(Suppliers, 'id', supplier_id)

        if not supplier.is_approved:
            msg = ORDERS_ERROR_RESPONSES['supplier_edit_validation_error']
            raise GraphQLError(msg)

        fields = cls.validate_fields(contacts, kwargs)

        for (key, value) in fields.items():
            if key is not None:
                setattr(supplier_contacts, key, value)

        with SaveContextManager(supplier_contacts,
                                model=SuppliersContacts) as supplier_contacts:
            name = supplier.name
            supplier.supplier_contacts = supplier_contacts
            supplier_contacts.save()
            msg = SUCCESS_RESPONSES["update_success"].format(
                f"Supplier '{name}'")
            return cls(supplier, msg)
