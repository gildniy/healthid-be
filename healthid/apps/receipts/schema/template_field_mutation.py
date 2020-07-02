import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.receipts.models import Receipt
from healthid.apps.receipts.schema.receipt_schema import ReceiptType
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class CreateFieldSet(graphene.Mutation):
    """
    Creates fields for template
    """
    field_set = graphene.Field(ReceiptType)

    class Arguments:
        cashier = graphene.String()
        discount_total = graphene.String()
        receipt_no = graphene.String()
        receipt = graphene.String()
        subtotal = graphene.String()
        total_tax = graphene.String()
        amount_to_pay = graphene.String()
        purchase_total = graphene.String()
        change_due = graphene.String()
        loyalty = graphene.String()
        loyalty_earned = graphene.String()
        loyalty_balance = graphene.String()
        barcode = graphene.String()
        footer = graphene.String()
        receipt_template_id = graphene.String()
        sale_id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        field_set = Receipt()
        for(key, value) in kwargs.items():
            setattr(field_set, key, value)
        with SaveContextManager(field_set, model=Receipt) as field_set:
            return CreateFieldSet(field_set=field_set)


class UpdateFieldSet(graphene.Mutation):
    """
    Updates a receipt template
    """
    field_set = graphene.Field(ReceiptType)

    class Arguments:
        id = graphene.String()
        cashier = graphene.String()
        discount_total = graphene.String()
        receipt_no = graphene.String()
        receipt = graphene.String()
        subtotal = graphene.String()
        total_tax = graphene.String()
        amount_to_pay = graphene.String()
        purchase_total = graphene.String()
        change_due = graphene.String()
        loyalty = graphene.String()
        loyalty_earned = graphene.String()
        loyalty_balance = graphene.String()
        barcode = graphene.String()
        footer = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        id = kwargs.get('id')
        field_set = get_model_object(Receipt, 'id', id)
        update_values = []
        for(key, value) in kwargs.items():
            setattr(field_set, key, value)
            if key == 'id':
                continue
            update_values.append(key)
        field_set.save(update_fields=update_values)
        return UpdateFieldSet(field_set=field_set)


class DeleteFieldSet(graphene.Mutation):
    """
    Deletes fieldSet
    """
    id = graphene.String()
    success = graphene.String()

    class Arguments:
        id = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, id):
        user = info.context.user
        field_set = get_model_object(Receipt, 'id', id)
        field_set.delete(user)
        return DeleteFieldSet(
               success=SUCCESS_RESPONSES[
                       "deletion_success"].format("FieldSet"))
