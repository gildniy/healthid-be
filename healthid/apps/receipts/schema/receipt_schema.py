import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from healthid.apps.receipts.models import ReceiptTemplate, Receipt
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.authentication.schema.queries.auth_queries import UserType


class ReceiptTemplateType(DjangoObjectType):
    class Meta:
        model = ReceiptTemplate


class ReceiptType(DjangoObjectType):
    cashier = graphene.Field(UserType)
    change_due = graphene.Float()
    receipt_no = graphene.String()
    discount_total = graphene.Float()
    sub_total = graphene.Float()
    total_tax = graphene.Float()
    amount_to_pay = graphene.Float()
    purchase_total = graphene.Float()
    loyalty = graphene.Int()
    loyalty_earned = graphene.Int()
    loyalty_balance = graphene.Int()
    barcode = graphene.String()
    footer = graphene.String()
    class Meta:
        model = Receipt

    def resolve_cashier(self, info, **kwargs):
        """
        gets cashier of the sale

        Returns:
            obj: user object to identify customer
        """
        return self.cashier

    def resolve_change_due(self, info, **kwargs):
        """
        gets change of customer

        Returns:
            decimal: how much change is given back to the customer
        """
        return self.change_due

    def resolve_receipt_no(self, info, **kwargs):
        """
        gets receipt number

        Returns:
            string: receipt unique identifier
        """
        if self.receipt_template.receipt_no:
            return self.receipt_no
        return None

    def resolve_footer(self, info, **kwargs):
        if self.receipt_template.footer_message:
            return self.receipt_template.footer_message
            
    def resolve_discount_total(self, info, **kwargs):
        """
        gets discount on receipt

        Returns:
            decimal: discount of sale
        """
        return self.discount_total

    def resolve_sub_total(self, info, **kwargs):
        """
        gets sub total on receipt

        Returns:
            decimal: sub total on receipt
        """
        return self.sub_total

    def resolve_total_tax(self, info, **kwargs):
        """
        gets total tax on receipt

        Returns:
            decimal: total tax on receipt
        """
        return self.total_tax

    def resolve_amount_to_pay(self, info, **kwargs):
        """
        gets amount to pay on receipt

        Returns:
            decimal: amount to be paid on receipt
        """
        return self.amount_to_pay

    def resolve_purchase_total(self, info, **kwargs):
        """
        gets purchase total for receipt

        Returns:
            decimal: total of discount and subtotal
        """
        return self.purchase_total

    def resolve_loyalty(self, info, **kwargs):
        """
        gets customer's loyalty status

        Returns:
            boolean: loyalty status of customer
        """
        return self.loyalty

    def resolve_loyalty_earned(self, info, **kwargs):
        """
        gets loyalty points a customer earned

        Returns:
            integer: loyalty points a customer earned during sale
        """
        return self.loyalty_earned

    def resolve_loyalty_balance(self, info, **kwargs):
        """
        gets loyalty points of customer

        Returns:
            integer: loyalty points of customer
        """
        return self.loyalty_balance

    def resolve_barcode(self, info, **kwargs):
        """
        gets barcode of receipt

        Returns:
            string: url of a receipt
        """
        if self.receipt_template.barcode:
            return self.barcode_url
        return None


class Query(graphene.ObjectType):
    """
    Return a list of receipt templates
    Or a single receipt template.
    """
    receipt_templates = graphene.List(ReceiptTemplateType)
    receipt_template = graphene.Field(ReceiptTemplateType, id=graphene.String(
    ), cashier=graphene.Boolean(), discount_total=graphene.Boolean(
    ), receipt_no=graphene.Boolean(), receipt=graphene.Boolean(
    ), subtotal=graphene.Boolean(), total_tax=graphene.Boolean(
    ), amount_to_pay=graphene.Boolean(), purchase_total=graphene.Boolean(
    ), change_due=graphene.Boolean(), loyalty=graphene.Boolean(
    ), loyalty_earned=graphene.Boolean(), loyalty_balance=graphene.Boolean(
    ), barcode=graphene.Boolean(), outlet_id=graphene.Int())
    receipts = graphene.List(ReceiptType)
    receipt = graphene.Field(ReceiptType,
                             receipt_id=graphene.String(required=True))

    @login_required
    def resolve_receipt_templates(self, info, **kwargs):
        return ReceiptTemplate.objects.all()

    @login_required
    def resolve_receipt_template(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return get_model_object(ReceiptTemplate, 'id', id)
        return None

    @login_required
    def resolve_receipts(self, info, **kwargs):
        """
        gets all receipts

        Returns:
            list: receipts objects
        """
        return Receipt.objects.all()

    @login_required
    def resolve_receipt(self, info, **kwargs):
        """
        gets a single receipt

        Returns:
            obj: receipt object
        """
        return get_model_object(Receipt, 'id', kwargs.get('receipt_id'))
