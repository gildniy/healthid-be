import csv
import graphene
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.dateparse import parse_date
from functools import reduce
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from io import StringIO

from healthid.apps.consultation.models import CustomerConsultation
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product
from healthid.apps.products.schema.product_query import ProductType
from healthid.apps.receipts.models import Receipt
from healthid.apps.receipts.schema.receipt_schema import ReceiptType
from healthid.apps.sales.models import (SalesPrompt, Sale, SaleReturn, SalesPerformance, Payments)
from healthid.apps.sales.schema.sales_query import SalePerformanceType
from healthid.apps.sales.schema.sales_schema import (
    ConsultationPaymentType, SalesPromptType,
    SaleType, SaleReturnType)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.sales_responses import (SALES_ERROR_RESPONSES,
                                                     SALES_SUCCESS_RESPONSES,
                                                     SALE_METHODS_MAP)
from django.template.loader import render_to_string


class CreateSalesPerformance(graphene.Mutation):
    """
    This creates a new entry into the sales performance
    """
    sale_performance = graphene.Field(SalePerformanceType)
    message = graphene.String()

    class Arguments:
        sale_id = graphene.Int(required=True)
        product_id = graphene.Int(required=True)
        cashier_id = graphene.String(required=True)
        customer_id = graphene.Int(required=True)
        outlet_id = graphene.Int(required=True)

        unit_price = graphene.Int(required=True)
        quantity_sold = graphene.Int(required=True)
        discount = graphene.Int(required=True)
        subtotal = graphene.Int(required=True)
        transaction_date = graphene.DateTime(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        new_sale_performance = SalesPerformance()

        for key, value in kwargs.items():
            setattr(new_sale_performance, key, value)

        with SaveContextManager(new_sale_performance, model=SalesPerformance) as new_sale_performance:
            message = SUCCESS_RESPONSES["creation_success"].format("Sale Performance")
            return CreateSalesPerformance(message=message, sale_performance=new_sale_performance)


class CreateSalesPrompts(graphene.Mutation):
    """
    This Creates a Sales Prompt for a group of products particular Product
    """
    sales_prompts = graphene.List(SalesPromptType)
    message = graphene.String()

    class Arguments:
        prompt_titles = graphene.List(graphene.String, required=True)
        descriptions = graphene.List(graphene.String, required=True)
        product_ids = graphene.List(graphene.Int, required=True)
        outlet_ids = graphene.List(graphene.Int, required=True)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        product_ids = kwargs.get('product_ids')
        titles = kwargs.get('prompt_titles')
        prompt_descriptions = kwargs.get('descriptions')
        outlet_ids = kwargs.get('outlet_ids')
        sales_prompt_count = 0
        valid_list = all(len(product_ids) == len(list_inputs)
                         for list_inputs in
                         [titles, prompt_descriptions, outlet_ids])

        if not valid_list or len(product_ids) < 1:
            raise GraphQLError(SALES_ERROR_RESPONSES["incomplete_list"])

        for title, description in zip(titles, prompt_descriptions):
            if title.strip() == "" or description.strip() == "":
                raise GraphQLError(SALES_ERROR_RESPONSES["title_error"])
        created_prompts = []
        for index, title in enumerate(titles, 0):
            params = {'model': SalesPrompt}
            sales_prompt = SalesPrompt(
                prompt_title=title.title(),
                description=prompt_descriptions[index],
                product_id=get_model_object(Product, 'id',
                                            product_ids[index]).id,
                outlet_id=get_model_object(Outlet, 'id',
                                           outlet_ids[index]).id)

            with SaveContextManager(sales_prompt, **params) as sales_prompt:
                created_prompts.append(sales_prompt)
                sales_prompt_count += 1

        return CreateSalesPrompts(
            sales_prompts=created_prompts,
            message=SUCCESS_RESPONSES[
                "creation_success"].format(
                "Sales prompt " + str(
                    sales_prompt_count)))


class UpdateSalesPrompt(graphene.Mutation):
    """
    This Updates a Sales prompt
    """
    success = graphene.String()
    salesPrompt = graphene.Field(SalesPromptType)

    class Arguments:
        id = graphene.Int(required=True)
        prompt_title = graphene.String()
        description = graphene.String()
        product_id = graphene.Int()
        outlet_id = graphene.Int()

    @login_required
    @user_permission('Manager')
    def mutate(self, info, id, **kwargs):
        salesPrompt = get_model_object(SalesPrompt, 'id', id)
        for key, value in kwargs.items():
            if key in ["prompt_title", "description"]:
                if value.strip() == "":
                    raise GraphQLError(SALES_ERROR_RESPONSES["title_error"])
            setattr(salesPrompt, key, value)
        params = {'model': SalesPrompt}
        with SaveContextManager(salesPrompt, **params) as salesPrompt:
            return UpdateSalesPrompt(
                success=SUCCESS_RESPONSES[
                    "update_success"].format("Sales prompt"),
                salesPrompt=salesPrompt)


class DeleteSalesPrompt(graphene.Mutation):
    """
    This deletes a Sales prompt
    """
    id = graphene.Int()
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission('Manager')
    def mutate(self, info, id):
        user = info.context.user
        prompt = get_model_object(SalesPrompt, 'id', id)
        prompt.delete(user)
        return DeleteSalesPrompt(
            success=SUCCESS_RESPONSES[
                "deletion_success"].format("Sales prompt"))


class Batches(graphene.InputObjectType):
    """
    This class defines necessary fields of a product to be sold
    Arguments:
        batch_id : The ID of the product batch
        quantity : the quantity 
        discount : The dicount involved
        price : The price of the product sold
    """
    batch_id = graphene.ID()
    product_id = graphene.ID()
    quantity = graphene.Int()
    discount = graphene.Float()
    price = graphene.Float()


class PaymentDetails(graphene.InputObjectType):
    """
    This class defines necessary fields indicating 
    the details of the different payment methods used for a sale
    Arguments:
        payment_method : The method of payment
        amount : The amount rendered using this particular method
    """
    payment_method = graphene.String()
    amount = graphene.Int()


class CreateSale(graphene.Mutation):
    """
    Create a sale
    """
    sale = graphene.Field(SaleType)
    message = graphene.String()
    error = graphene.String()
    receipt = graphene.Field(ReceiptType)
    products = graphene.List(ProductType)

    class Arguments:
        customer_id = graphene.String()
        outlet_id = graphene.Int(required=True)
        batches = graphene.List(Batches, required=True)
        discount_total = graphene.Float(graphene.Float, required=True)
        sub_total = graphene.Float(graphene.Float, required=True)
        amount_to_pay = graphene.Float(graphene.Float, required=True)
        paid_amount = graphene.Float(graphene.Float, required=True)
        change_due = graphene.Float(graphene.Float, required=True)
        payment_method = graphene.String(graphene.String, required=True)
        payments_made = graphene.List(PaymentDetails)
        notes = graphene.String()
        return_sale_id = graphene.Int()

    @staticmethod
    def mutation_helper(info, **kwargs):
        payments_made = kwargs.get("payments_made")

        # check the length of payments made to determine if only one payment method was used
        if len(payments_made) == 1:
            kwargs['payment_method'] = SALE_METHODS_MAP[payments_made[0]['payment_method']]
        else:
            kwargs['payment_method'] = "Split"

            # make the sale
        new_sale = Sale()
        new_receipt = Receipt()
        sale = new_sale.create_sale(info=info, **kwargs)
        receipt = new_receipt.create_receipt(sale, kwargs.get('outlet_id'))
        product_ids = list(map((lambda batch: batch.product_id), kwargs.get('batches')))
        products = Product.objects.filter(id__in=product_ids)

        # create entries into the payments table if the sale was sucesfully made
        if payments_made:
            for payment in payments_made:
                if sale.return_sale_id:
                    payment['amount'] *= -1
                new_payment = Payments(
                    sale=sale,
                    payment_method=payment['payment_method'],
                    amount=payment['amount']
                )
                new_payment.save()
        return [sale, receipt, products]

    @login_required
    def mutate(self, info, **kwargs):
        [sale, receipt, products] = CreateSale.mutation_helper(info, **kwargs)
        return CreateSale(sale=sale,
                          receipt=receipt,
                          message=SALES_SUCCESS_RESPONSES["create_sales_success"],
                          products=products
                          )


class CreateReturn(CreateSale):
    old_sale = graphene.Field(SaleType)
    new_return = graphene.Field(SaleType)

    class Arguments(CreateSale.Arguments):
        return_sale_id = graphene.Int(required=True)

    @login_required
    def mutate(self, info, **kwargs):
        old_sale = Sale.objects.get(id=kwargs['return_sale_id'])
        if not old_sale:
            raise GraphQLError(SALES_ERROR_RESPONSES['sales_does_not_exist'])
        [sale, receipt, products] = CreateReturn.mutation_helper(info, **kwargs)
        return CreateReturn(new_return=sale,
                            receipt=receipt,
                            message=SALES_SUCCESS_RESPONSES["sales_return_approved"],
                            products=products,
                            old_sale=old_sale
                            )


class ConsultationPayment(graphene.Mutation):
    """
    Make payment for a consultation
    Args:
        customer_consultation_id (id) id of the consultation item
        discount_total (float) discount given if any
        sub_total (float) sale subtotal
        paid_amount (float) amount client has given
        change_due (float) change due to client
        payment_method (str) payment option chosen
        notes (str) Narrative for the sale
    returns:
         sale object for the consultation,
         otherwise a GraphqlError is raised
    """
    sale = graphene.Field(ConsultationPaymentType)
    message = graphene.String()
    receipt = graphene.Field(ReceiptType)

    class Arguments:
        customer_consultation_id = graphene.Int(required=True)
        discount_total = graphene.Float(graphene.Float, required=True)
        sub_total = graphene.Float(graphene.Float, required=True)
        paid_amount = graphene.Float(graphene.Float, required=True)
        change_due = graphene.Float(graphene.Float, required=True)
        payment_method = graphene.String(graphene.String, required=True)
        notes = graphene.String()

    @login_required
    def mutate(self, info, **kwargs):
        user = info.context.user
        customer_consultation_id = kwargs.get('customer_consultation_id')
        customer_consultation = get_model_object(
            CustomerConsultation, 'id', customer_consultation_id)
        outlet = customer_consultation.outlet

        if customer_consultation.paid:
            raise GraphQLError(SALES_ERROR_RESPONSES["already_marked_as_paid"])

        price = customer_consultation.consultation_type.price_per_session
        new_sale = Sale(
            sales_person=user, customer=customer_consultation.customer,
            outlet=outlet,
            amount_to_pay=price)

        del kwargs['customer_consultation_id']
        for (key, value) in kwargs.items():
            setattr(new_sale, key, value)

        with SaveContextManager(new_sale, model=Sale) as new_sale:
            pass

        customer_consultation.paid = True
        customer_consultation.sale_record = new_sale
        customer_consultation.save()

        new_receipt = Receipt()
        receipt = new_receipt.create_receipt(new_sale, outlet.id)

        return ConsultationPayment(
            sale=new_sale, receipt=receipt, message='message')


class SalesReturnEnum(graphene.Enum):
    CustomerError = 'wrong product bought'
    RetailerError = 'Returned to Distributor'
    DamagedProduct = 'Damaged Product'
    ExpiredProduct = 'Expired Product'
    Others = 'Others'


class PayEnum(graphene.Enum):
    """
    This class defines choices for refund compensation type
    """
    Cash = 'cash'
    StoreCredit = 'store credit'


class ReturnedProducts(graphene.InputObjectType):
    """
    This class defines necessary fields of a product to be returned
    """
    batch_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True)
    price = graphene.Float(required=True)
    resellable = graphene.Boolean(required=True)
    return_reason = graphene.Argument(SalesReturnEnum, required=True)


class InitiateSaleReturn(graphene.Mutation):
    """
    initiate a sales return by user(Cashier, manager or accountant)
    """
    message = graphene.String()
    sales_return_initiated = graphene.Field(SaleReturnType)
    error = graphene.String()

    class Arguments:
        sale_id = graphene.Int(required=True)
        returned_batches = graphene.List(ReturnedProducts, required=True)
        outlet_id = graphene.Int(required=True)
        return_amount = graphene.Float(required=True)
        return_note = graphene.String()
        refund_compensation_type = graphene.Argument(PayEnum, required=True)

    @login_required
    def mutate(self, info, **kwargs):
        new_return = SaleReturn()
        return_initiated = new_return.create_return(
            user=info.context.user, **kwargs)
        return InitiateSaleReturn(
            message=SALES_SUCCESS_RESPONSES["sale_intiate_success"],
            sales_return_initiated=return_initiated)


class ApproveSalesReturn(graphene.Mutation):
    sales_return = graphene.Field(SaleReturnType)
    message = graphene.String()

    class Arguments:
        sales_return_id = graphene.Int(required=True)
        sales_id = graphene.Int(required=True)
        returned_sales = graphene.List(graphene.Int, required=True)

    @login_required
    @user_permission('Manager')
    def mutate(self, info, **kwargs):
        sales_id = kwargs.get('sales_id')
        returned_sales = kwargs.get('returned_sales')

        if not returned_sales:
            raise GraphQLError(SALES_ERROR_RESPONSES["empty_sales_return"])

        receipt = get_model_object(Receipt, 'sale_id', sales_id)

        new_return = SaleReturn()
        sales_return = new_return.approve_sales_return(
            user=info.context.user, receipt=receipt, **kwargs)

        return ApproveSalesReturn(
            sales_return=sales_return,
            message=SALES_SUCCESS_RESPONSES["sales_return_approved"])


class SellsReportType(graphene.InputObjectType):
    cashier = graphene.String(required=True)
    total = graphene.Float(required=True)
    cash = graphene.Float(required=True)
    card = graphene.Float(required=True)
    bank_transfer = graphene.Float(required=True)
    store_credit = graphene.Float(required=True)
    date_time = graphene.String(required=True)


class SendSellsReportEmail(graphene.Mutation):
    message = graphene.String()
    from_email = settings.DEFAULT_FROM_EMAIL
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    class Arguments:
        to_emails = graphene.List(graphene.String, required=True)
        sells = graphene.List(SellsReportType, required=True)

    @login_required
    def mutate(self, info, **kwarg):
        datetime_string = SendSellsReportEmail.dt_string
        subject = 'Sells Report ' + datetime_string
        body = 'Find here attached the Sells report file: ' + datetime_string
        to_emails = kwarg.get('to_emails')

        message = {
            'body': body,
            'date': datetime_string
        }

        template = 'email_alerts/sales_report/sales_report_email_with_attachment.html'
        html_body = render_to_string(template, {'message': message})

        message = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=SendSellsReportEmail.from_email,
            to=to_emails
        )

        message.content_subtype = 'html'

        attachment_csv_file = StringIO()
        sells = kwarg.get('sells')
        fieldnames = list(sells[0].keys())
        writer = csv.DictWriter(attachment_csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sells)

        message.attach('health_id_sells_report_' + SendSellsReportEmail.now.strftime("%Y-%m-%d-%H:%M:%S") + '.csv',
                       attachment_csv_file.getvalue(), 'text/csv')

        message.send(fail_silently=False)

        return SendSellsReportEmail(message='Sells report with attachment file sent successfully')


class Mutation(graphene.ObjectType):
    create_salesprompts = CreateSalesPrompts.Field()
    delete_salesprompt = DeleteSalesPrompt.Field()
    update_salesprompt = UpdateSalesPrompt.Field()
    create_sale = CreateSale.Field()
    create_return = CreateReturn.Field()
    consultation_payment = ConsultationPayment.Field()
    initiate_sales_return = InitiateSaleReturn.Field()
    approve_sales_return = ApproveSalesReturn.Field()
    create_sales_performance = CreateSalesPerformance.Field()
    send_sells_report_email = SendSellsReportEmail.Field()
