from django.db import models
from decimal import Decimal
from graphql import GraphQLError
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Sum, Count
from django.db.models.signals import pre_save

from healthid.apps.orders.models.orders import ProductBatch
from healthid.utils.app_utils.get_user_business import get_user_business

from healthid.apps.authentication.models import User
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product, BatchInfo
from healthid.apps.profiles.models import Profile

from healthid.models import BaseModel

from healthid.apps.preference.models import OutletPreference
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.app_utils.id_generator import id_gen
from healthid.utils.sales_utils.initiate_sale import initiate_sale
from healthid.utils.sales_utils.validate_sale import SalesValidator
from healthid.utils.sales_utils.validators import check_approved_sales
from healthid.apps.wallet.models import (
    CustomerCredit, StoreCreditWalletHistory)
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES
from healthid.apps.authentication.models import User
from healthid.apps.profiles.models import Profile


class PromotionType(BaseModel):
    id = models.CharField(max_length=9, primary_key=True,
                          default=id_gen, editable=False)
    name = models.CharField(max_length=140, unique=True)

    def __str__(self):
        return self.name


class Promotion(BaseModel):
    id = models.CharField(max_length=9, primary_key=True,
                          default=id_gen, editable=False)
    title = models.CharField(max_length=140, unique=True)
    promotion_type = models.ForeignKey(PromotionType, on_delete=models.CASCADE)
    description = models.TextField()
    applied_date = models.DateField(
        auto_now=False, auto_now_add=False, null=True)
    products = models.ManyToManyField(Product, blank=True)
    discount = models.DecimalField(decimal_places=2, max_digits=10)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class SalesPrompt(BaseModel):
    prompt_title = models.CharField(max_length=244, unique=True)
    description = models.CharField(
        max_length=244, default="Sales prompt descripttion:")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)

    def __str__(self):
        return self.prompt_title


class Cart(models.Model):
    '''
    defines cart model.
    args:
        user: owner of the cart.
        items: products along with the quantity and their total that
               have been added to the cart
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('CartItem')

    @property
    def total(self):
        '''
        method that calculates the total price of all the items in cart
        '''
        return self.items.all().aggregate(Sum('item_total'))['item_total__sum']


class CartItem(models.Model):
    '''
    defines cart item model
    args:
        product: product to be added to cart
        quantity: amount of product to be added to cart
        item_total: price of the product based on the quantity
    '''
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    item_total = models.DecimalField(default=0.00,
                                     max_digits=10,
                                     decimal_places=2)

    def __str__(self):
        return str(self.id)


def update_item_total(**kwargs):
    """
    function that calculates the price of product being added to cart
    based on the quantity being added, this is triggered before a cart
    item is saved
    """
    cart_item = kwargs.get('instance')
    cart_item.item_total = \
        cart_item.product.sales_price * cart_item.quantity


pre_save.connect(update_item_total, sender=CartItem)


class Sale(BaseModel):
    """
    Defines sale model
    Attributes:
            sales_person: Holds employee who made the transaction
            outlet: Holds outlet referencing id.
            customer: Holds a customer who bought the drugs if provided..
            sub_total: Holds the total minus discount.
            amount_to_pay = Holds the total amount including discounts.
            paid_cash  = Holds the paid cash amount
            change_due = Holds the remaining balance
            payment_method: Holds payment method e.g. cash/cash
            notes: Holds note about the sale
    """
    CASH = 'Cash'
    CREDIT = 'Credit'
    CARD = 'Card'
    BANK_TRANSFER = 'Bank_Transfer'
    SPLIT = 'Split'
    PAYMENT_METHODS = (
    (CASH, 'Cash'), (CREDIT, 'Credit'), (CARD, 'Card'), (BANK_TRANSFER, 'Bank_Transfer'), (SPLIT, 'Split'))
    sales_person = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sold_by')
    customer = models.ForeignKey(
        Profile, on_delete=models.CASCADE, null=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    amount_to_pay = models.DecimalField(max_digits=12, decimal_places=2)
    discount_total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    change_due = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        choices=PAYMENT_METHODS,
        max_length=18)
    notes = models.TextField(blank=True, null=True)
    loyalty_earned = models.PositiveIntegerField(default=0)
    return_sale_id = models.IntegerField(default=0)

    def _validate_sales_details(self, **kwargs):
        """
        This method handles all validations related to sale fields
        Arguments:
            kwargs: information about sale
        """
        sold_batches = kwargs.get('batches')
        sales_validator = SalesValidator(sold_batches)
        sales_validator.check_sales_fields_validity(**kwargs)
        sales_validator.check_validity_of_ids()
        sales_validator.check_product_discount()
        sales_validator.check_product_price()
        sales_validator.check_payment_method(**kwargs)
        sold_product_instances = sales_validator.check_validity_quantity_sold()
        return sold_product_instances

    @property
    def get_default_register(self):
        """
        Returns a default register for each outlet
        """
        try:
            register = self.outlet.outlet_register.all().first()
            return register.id
        except ObjectDoesNotExist:
            return None

    @property
    def get_split_payments(self):
        """
        Returns the split payments breakdown
        """
        return Payments.objects.filter(
            sale_id=self.id
        )

        pass

    def create_sale(self, info, **kwargs):
        """
        This method create a sale after it has been validated
        by _validate_sales_details()
        Arguments:
            kwargs: information about sale
            info: information about the logged in user
        """
        sales_person = info.context.user

        customer_id = kwargs.get('customer_id')
        outlet_id = kwargs.get('outlet_id')
        sold_batches = kwargs.get('batches')
        discount_total = kwargs.get('discount_total')
        sub_total = kwargs.get('sub_total')
        amount_to_pay = kwargs.get('amount_to_pay')
        paid_amount = kwargs.get('paid_amount')
        payment_method = kwargs.get('payment_method')
        change_due = kwargs.get('change_due')
        notes = kwargs.get('notes')
        return_sale_id = kwargs.get('return_sale_id') if kwargs.get('return_sale_id') else 0
        if return_sale_id:
            discount_total = 0
            sub_total *= -1
            paid_amount *= -1
            amount_to_pay *= -1
        outlet = get_model_object(Outlet, "id", outlet_id)
        sold_product_instances = Sale._validate_sales_details(
            self, **kwargs)
        sale = Sale(sales_person=sales_person,
                    outlet=outlet,
                    payment_method=payment_method,
                    discount_total=discount_total,
                    sub_total=sub_total,
                    amount_to_pay=amount_to_pay,
                    paid_amount=paid_amount,
                    change_due=change_due,
                    notes=notes,
                    return_sale_id=return_sale_id)
        customer = None
        if customer_id:
            customer = get_model_object(Profile, "id", customer_id)
            if payment_method == 'credit':
                customer_credit = get_model_object(
                    CustomerCredit, "customer", customer.id)
                outlet_preference = get_model_object(
                    OutletPreference, "outlet", outlet_id)
                if outlet_preference.outlet_currency_id != (
                        customer_credit.credit_currency_id):
                    raise GraphQLError(
                        SALES_ERROR_RESPONSES['wrong_currency'])
                if customer_credit.store_credit < amount_to_pay:
                    raise GraphQLError(
                        SALES_ERROR_RESPONSES['less_credit'])
                customer_credit.store_credit = (
                        customer_credit.store_credit - Decimal(amount_to_pay))
                customer_credit.save()
                debit_wallet_history = StoreCreditWalletHistory(
                    sales_person=sales_person,
                    debit=amount_to_pay,
                    current_store_credit=customer_credit.store_credit,
                    customer_account=customer_credit)
                debit_wallet_history.save()

        with SaveContextManager(sale) as sale:
            loyalty_points_earned = initiate_sale(
                sold_product_instances,
                sold_batches,
                sale,
                SaleDetail,
                BatchHistory)
            if customer_id:
                sale.customer = customer
                if customer.loyalty_member:
                    sale.loyalty_earned = loyalty_points_earned
                    customer.loyalty_points += loyalty_points_earned
                    customer.save()
                sale.save()
        return sale

    def sales_history(self, outlet_id=None, search=None, \
                      date_from=None, date_to=None):
        sales = Sale.objects.filter(outlet_id=outlet_id)

        if search:
            search_keys = (
                    Q(customer__first_name__icontains=search) |
                    Q(customer__last_name__icontains=search) |
                    Q(sales_person__first_name__icontains=search) |
                    Q(sales_person__last_name__icontains=search) |
                    Q(customer__email__icontains=search) |
                    Q(saledetail__product__product_name__icontains=search) |
                    Q(notes__icontains=search)
            )
            sales = list(set(sales.filter(search_keys)))

        date_from_sales = []

        if date_from:
            for sale in sales:
                if sale.created_at >= date_from:
                    date_from_sales.append(sale)
            date_to_sales = []
            if date_to:
                for sale in date_from_sales:
                    if sale.created_at <= date_to:
                        date_to_sales.append(sale)
                return date_to_sales
            return date_from_sales

        return sales

    class Meta:
        ordering = ['-created_at']


class SaleDetail(BaseModel):
    """
    Defines sale detail model
    Attributes:
        product: Holds a reference to products to be sold
        sale:  Holds a sale reference to this product
        quantity:  Holds the quantity to be sold of a product
        price: Holds the price for each product
        note: Holds note about the product
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch_id = models.CharField(max_length=50, null=True)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    discount = models.FloatField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True, null=True)

    @property
    def get_batch(self):
        return ProductBatch.objects.get(id=self.batch_id)


class SaleReturn(BaseModel):
    """
    Defines sale return model
    Attributes:
        cashier(obj): Holds employee id who made the return initiation
        customer(obj): Holds customer who earlier bought if provided
        sale(obj): Holds id of sale reference to this product
        outlet(int): Holds the outlet id
        return_note(str): Holds note for return reason
        return_amount(float): Holds the amount to return the customer
        refund_compensation_type(str): Either cash or store credit.
    """
    cashier = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='cashier', null=True)
    customer = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True)
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.SET_NULL, null=True)
    return_note = models.CharField(max_length=80, blank=True)
    return_amount = models.DecimalField(max_digits=12, decimal_places=2)
    refund_compensation_type = models.CharField(max_length=80)

    def create_return(self, user, **kwargs):
        """This function initiates a return of products sold
        Args:
            user: the logged in user
            sale_id(int): id referencing that sale we are returning from
            outlet_id(int): outlet we are returning to to
            sale_id(int): id referencing that sale we are returning from
            return_amount(int): pay back amount to user for goods returned
            return_note(str): Holds return reason about the product
            returned_products(objs): Holds products being returned
            refund_compensation_type(str): Either cash or store credit


        Returns:
            salereturn(obj): which is saved in the table sale.salereturn

        """
        cashier = user
        sales_instance = get_model_object(
            Sale, 'id', kwargs.get('sale_id'))
        customer = sales_instance.customer
        outlet_instance = get_model_object(
            Outlet, 'id', kwargs.get('outlet_id'))
        return_validator = SalesValidator(kwargs.get('returned_batches'))
        return_validator.check_product_returnable()
        return_validator.check_product_dates_for_return(
            outlet_instance, sales_instance)

        sales_return = SaleReturn(
            cashier=cashier, customer=customer, sale=sales_instance)
        for (key, value) in kwargs.items():
            setattr(sales_return, key, value)
        with SaveContextManager(sales_return, model=SaleReturn)as sales_return:
            pass
        sale_return_detail_list = []
        for batch in kwargs.get('returned_batches'):
            batch_instance = get_model_object(
                BatchInfo, 'id', batch.batch_id)
            sales_return_detail = SaleReturnDetail(
                batch=batch_instance,
                sales_return=sales_return,
                quantity=batch.quantity,
                price=batch.price,
                resellable=batch.resellable,
                return_reason=batch.return_reason
            )
            sale_return_detail_list.append(sales_return_detail)
        SaleReturnDetail.objects.bulk_create(sale_return_detail_list)
        return sales_return

    def approve_sales_return(self, user, receipt, **kwargs):
        returned_sales = kwargs.get('returned_sales')
        sales_id = kwargs.get('sales_id')
        sales_return_id = kwargs.get('sales_return_id')

        sales_return = get_model_object(SaleReturn, 'id', sales_return_id)

        check_approved_sales(returned_sales, SaleReturnDetail)

        for returned_sale in returned_sales:
            returned_sale_detail = get_model_object(
                SaleReturnDetail, 'id', returned_sale)
            batch_histories = BatchHistory.objects. \
                filter(sale_id=sales_id,
                       batch_info_id=returned_sale_detail.batch_id)

            returned_quantity = returned_sale_detail.quantity

            self.return_batch_quantity(batch_histories, receipt,
                                       returned_quantity, returned_sale_detail,
                                       sales_return_id, user)
        return sales_return

    def return_batch_quantity(self, batch_histories, receipt,
                              returned_quantity, returned_sale_detail,
                              sales_return_id, user):
        for batch_history in batch_histories:
            batch = get_model_object(BatchInfo, 'id',
                                     batch_history.batch_info.id)

            quantity = batch.batch_quantities.filter(
                is_approved=True).first()

            if returned_sale_detail.resellable:
                quantity.quantity_remaining += returned_quantity
                quantity.save()
            returned_sale_detail.is_approved = True
            returned_sale_detail.done_by = user
            returned_sale_detail.save()
        receipt.sales_return_id = sales_return_id
        receipt.save()


class SaleReturnDetail(BaseModel):
    """
    Defines return detail model
    Attributes:
        batch(obj): Holds a reference to the batch to be returned
        sales_return(obj): Holds a sale return reference to this product
        quantity(int):  Holds the quantity to be sold of a product
        price(float): Holds the price for each product
        return_reason(str): Holds enum return reason about the product
        is_approved(bool): Holds boolean for particular product return approved
    """
    batch = models.ForeignKey(BatchInfo, on_delete=models.SET_NULL, null=True)
    sales_return = models.ForeignKey(
        SaleReturn, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    return_reason = models.CharField(max_length=80)
    is_approved = models.BooleanField(default=False)
    resellable = models.BooleanField(default=False)

    def __str__(self):
        return self.return_reason


class BatchHistory(BaseModel):
    batch_info = models.ForeignKey(
        BatchInfo, on_delete=models.SET_NULL, null=True,
        related_name='batch_info_history')
    sale = models.ForeignKey(
        Sale, on_delete=models.SET_NULL, null=True,
        related_name='sale_batch_history')
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True,
        related_name='quantity_by_batches')
    quantity_taken = models.PositiveIntegerField()

    def team_performance(self, business, date_today_before, date_today_after):

        sales = BatchHistory.objects.filter(created_at__gte=date_today_before).filter(
            created_at__lte=date_today_after)

        users_sales = []

        for sale in sales:
            if not any(user.sale.sales_person == sale.sale.sales_person for user in users_sales) and get_user_business(
                    sale.sale.sales_person) == business:
                sale.totalProductsSold = sales.filter(sale__sales_person=sale.sale.sales_person).aggregate(
                    Count('product__product_name', distinct=True))['product__product_name__count'] or 0

                sale.totalQtySold = sales.filter(sale__sales_person=sale.sale.sales_person).aggregate(
                    Sum('quantity_taken'))['quantity_taken__sum'] or 0

                sale.totalCashAmount = sales.filter(sale__sales_person=sale.sale.sales_person).filter(
                    sale__payment_method='cash').aggregate(Sum('sale__paid_amount'))['sale__paid_amount__sum'] or 0

                sale.totalCardAmount = sales.filter(sale__sales_person=sale.sale.sales_person).filter(
                    sale__payment_method='card').aggregate(Sum('sale__paid_amount'))['sale__paid_amount__sum'] or 0

                users_sales.append(sale)

        return users_sales


class SalesPerformance(BaseModel):
    sale = models.ForeignKey(
        Sale, on_delete=models.CASCADE, related_name="sales")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="sale_product")
    cashier = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sale_cashier")
    outlet = models.ForeignKey(
        Outlet, on_delete=models.CASCADE, related_name="sale_performance")
    customer = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="sale_customer", null=True)
    unit_price = models.PositiveIntegerField()
    quantity_sold = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()
    transaction_date = models.DateTimeField()


class Payments(BaseModel):
    """
    defines a model which stores the different payment methods associated with a sale
    Args:
        sale : the sale
        payment_method : the method of this amount
        amount : the amount associated with this payment method
    """
    CASH = "CASH"
    CARD = "CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    STORE_CREDIT = "STORE_CREDIT"

    PAYMENTS_METHODS = (
        (CASH, "The Payment method involving cash"),
        (CARD, "The Payment method involving card"),
        (BANK_TRANSFER, "The Payment method involving transfer to bank"),
        (STORE_CREDIT, "The Payment method involving store credits"),
    )

    sale = models.ForeignKey(
        Sale, on_delete=models.CASCADE)
    payment_method = models.CharField(
        max_length=30, choices=PAYMENTS_METHODS, default=CASH
    )
    amount = models.DecimalField(decimal_places=2, max_digits=12, null=True)
