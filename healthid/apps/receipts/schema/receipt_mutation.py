import graphene

from graphql_jwt.decorators import login_required

from healthid.apps.receipts.models import ReceiptTemplate, Receipt
from healthid.apps.receipts.schema.receipt_schema import ReceiptTemplateType
from healthid.apps.receipts.schema.template_field_mutation import (
    CreateFieldSet, DeleteFieldSet, UpdateFieldSet)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.receipts_responses import \
    RECEIPT_SUCCESS_RESPONSES


class CreateReceiptTemplate(graphene.Mutation):
    """
    Creates a receipt template
    """
    receipt_template = graphene.Field(ReceiptTemplateType)

    class Arguments:
        cashier = graphene.Boolean()
        discount_total = graphene.Boolean()
        receipt_no = graphene.Boolean()
        receipt = graphene.Boolean()
        subtotal = graphene.Boolean()
        total_tax = graphene.Boolean()
        amount_to_pay = graphene.Boolean()
        purchase_total = graphene.Boolean()
        change_due = graphene.Boolean()
        loyalty = graphene.Boolean()
        loyalty_earned = graphene.Boolean()
        loyalty_balance = graphene.Boolean()
        barcode = graphene.Boolean()
        outlet_id = graphene.Int()
        footer_message = graphene.String()
        logo = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        receipt_template = ReceiptTemplate()
        for (key, value) in kwargs.items():
            setattr(receipt_template, key, value)
        with SaveContextManager(receipt_template) as receipt_template:
            return CreateReceiptTemplate(receipt_template=receipt_template)


class UpdateReceiptTemplate(graphene.Mutation):
    """
    Updates a receipt template
    """
    receipt_template = graphene.Field(ReceiptTemplateType)

    class Arguments:
        id = graphene.String(required=True)
        cashier = graphene.Boolean()
        discount_total = graphene.Boolean()
        receipt_no = graphene.Boolean()
        receipt = graphene.Boolean()
        subtotal = graphene.Boolean()
        total_tax = graphene.Boolean()
        amount_to_pay = graphene.Boolean()
        purchase_total = graphene.Boolean()
        change_due = graphene.Boolean()
        loyalty = graphene.Boolean()
        loyalty_earned = graphene.Boolean()
        loyalty_balance = graphene.Boolean()
        barcode = graphene.Boolean()
        outlet_id = graphene.Int()
        footer_message = graphene.String()
        logo = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, id, **kwargs):
        receipt_template = get_model_object(ReceiptTemplate, 'id', id)
        for (key, value) in kwargs.items():
            setattr(receipt_template, key, value)
        receipt_template.save()
        return UpdateReceiptTemplate(receipt_template=receipt_template)


class DeleteReceiptTemplate(graphene.Mutation):
    """
    Deletes a receipt template
    """
    id = graphene.String()
    success = graphene.String()

    class Arguments:
        id = graphene.String()

    @login_required
    @user_permission()
    def mutate(self, info, id):
        user = info.context.user
        receipt_template = get_model_object(ReceiptTemplate, 'id', id)
        receipt_template.delete(user)
        return DeleteReceiptTemplate(
            success=SUCCESS_RESPONSES[
                "deletion_success"].format("Receipt template")
        )


class MailReceipt(graphene.Mutation):
    """
    Sends a receipt to a customer's email address

    Args:
        receipt_id (int):  Receipt ID

    returns:
         message: success message
    """
    message = graphene.String()

    class Arguments:
        receipt_id = graphene.String(required=True)

    @login_required
    def mutate(self, info, receipt_id):
        Receipt.mail_receipt(receipt_id)
        return MailReceipt(message=RECEIPT_SUCCESS_RESPONSES["mailer_success"])


class Mutation(graphene.ObjectType):
    create_receipt_template = CreateReceiptTemplate.Field()
    update_receipt_template = UpdateReceiptTemplate.Field()
    delete_receipt_template = DeleteReceiptTemplate.Field()
    mail_receipt = MailReceipt.Field()
    create_field_set = CreateFieldSet.Field()
    update_field_set = UpdateFieldSet.Field()
    delete_field_Set = DeleteFieldSet.Field()
