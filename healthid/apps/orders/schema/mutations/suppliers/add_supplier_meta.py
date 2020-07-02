import graphene
from graphql.error import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.schema.suppliers_query import (SuppliersMetaType)
from healthid.apps.orders.models import SuppliersMeta
from healthid.utils.app_utils.database import (SaveContextManager)
from healthid.apps.orders.enums.suppliers import PaymentTermsType
from healthid.utils.messages.common_responses import ERROR_RESPONSES


class SuppliersMetaInput(graphene.InputObjectType):
    supplier_id = graphene.String(required=True)
    display_name = graphene.String()
    credit_days = graphene.Int()
    logo = graphene.String()
    payment_terms = graphene.String(required=True)
    commentary = graphene.String()
    admin_comment = graphene.String()


class AddSupplierMeta(graphene.Mutation):
    """
    Add a new supplier to the database

    args:
        supplier_id(str): supplier ID
        display_name(str): supplier display_name
        credit_days(int): average number of days expected to
                          settle outstanding payments to the supplier
        logo(str): image URL for the supplier logo
        payment_terms(str): preferred payment method
                            (on credit or cash on delivery )
        commentary(str): additional comments
        admin_comment(str): additional admin comments

    returns:
        supplier_meta(obj): 'SuppliersMeta' model object detailing
                            the created supplier_meta.
    """

    class Arguments:
        input = SuppliersMetaInput(required=True)

    supplier_meta = graphene.Field(SuppliersMetaType)

    @classmethod
    def validate_fields(cls, input):
        fields = input
        fields['display_name'] = input['display_name'].strip(
        ) if input.get('display_name') else None
        fields['credit_days'] = fields.get('credit_days') or 0
        is_payment_term_valid = False
        payment_terms = fields['payment_terms'].upper().replace(' ', '_')
        for choice in PaymentTermsType.choices():
            is_payment_term_valid = payment_terms in choice
            if is_payment_term_valid:
                break

        if not is_payment_term_valid:
            raise GraphQLError(
                ERROR_RESPONSES['payment_terms'].format(
                    fields['payment_terms']))

        if payment_terms == 'ON_CREDIT' and fields['credit_days'] <= 0:
            raise GraphQLError(ERROR_RESPONSES['payment_terms_on_credit'])

        if payment_terms == 'CASH_ON_DELIVERY' and fields['credit_days'] > 0:
            raise GraphQLError(
                ERROR_RESPONSES['payment_terms_cash_on_deliver'])

        return fields

    @classmethod
    @login_required
    def mutate(cls, root, info, input=None):
        supplier_meta = SuppliersMeta()

        fields = cls.validate_fields(input)

        for (key, value) in fields.items():
            setattr(supplier_meta, key, value)
        with SaveContextManager(supplier_meta,
                                model=SuppliersMeta) as supplier_meta:
            return cls(supplier_meta=supplier_meta)
