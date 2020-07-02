from decimal import Decimal
from functools import reduce
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q, Sum
from django.forms.models import model_to_dict
from taggit.managers import TaggableManager

from healthid.apps.authentication.models import User
from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.outlets.models import Outlet
from healthid.apps.business.models import Business
from healthid.apps.products.managers import ProductManager, QuantityManager
from healthid.models import BaseModel
from healthid.utils.app_utils.id_generator import id_gen
from healthid.utils.app_utils.validator import validator

from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES
from healthid.utils.product_utils.product_price_checker import \
    round_off_selling_price


class ProductCategory(BaseModel):
    """
    model for product category

    Attributes:
        name: name to product category
        amount_paid: how much money to pay in order to earn a loyalty
                     point
        loyalty_weight: points attached to the purchase of products in
                        category
    """
    name = models.CharField(max_length=50)
    amount_paid = models.PositiveIntegerField(default=100)
    loyalty_weight = models.PositiveIntegerField(default=0)
    markup = models.PositiveIntegerField(default=25)
    is_vat_applicable = models.BooleanField(default=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ['name', 'business']


class DispensingSize(BaseModel):
    name = models.CharField(max_length=150, unique=True)


class Product(BaseModel):
    """
    model for products

    Attributes:
        is_returnable: boolean field makes all products initailly
                      returnable. According to preferences, the user
                      can change this for a particular product
                      to make it false.
        all_products: model manager returns both all products including
                      deactivated products i.e Products.all_products.all()
                      returns both active and deactivated products use it
                      when you need deactivate products as well.
        objects:  model manager returns only activated products i.e
        Products.objects.all() returns only active products use it when
        you don't need deactivated products.'''
    """
    product_category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(max_length=244, null=False)
    dispensing_size = models.ForeignKey(
        DispensingSize, on_delete=models.CASCADE, null=True)
    sku_number = models.CharField(max_length=100, null=True)
    is_approved = models.BooleanField(default=False)
    description = models.TextField()
    brand = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=50)
    vat_status = models.BooleanField(default=False)
    sales_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True)
    nearest_expiry_date = models.DateField(
        auto_now=False, auto_now_add=False, null=True)
    preferred_supplier = models.ForeignKey(
        Suppliers, related_name='prefered', null=True, on_delete=models.CASCADE)
    backup_supplier = models.ForeignKey(
        Suppliers, related_name='backup', null=True, on_delete=models.CASCADE)
    business = models.ForeignKey(
        Business, related_name='business_products',
        on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True,
        related_name='created_products')
    admin_comment = models.TextField(null=True)
    tags = TaggableManager()
    markup = models.PositiveIntegerField(default=25)
    auto_price = models.BooleanField(default=True)
    loyalty_weight = models.IntegerField(default=0)
    is_returnable = models.BooleanField(default=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="proposedEdit",
        null=True,
        blank=True)
    image = models.URLField(
        default='https://res.cloudinary.com/dojaopytm/image/upload/'
                'v1558444184/productPlaceholder.png')
    is_active = models.BooleanField(default=True)
    reorder_point = models.IntegerField(default=0)
    reorder_max = models.IntegerField(default=0)
    request_declined = models.BooleanField(default=False)
    global_upc = models.CharField(max_length=50, null=True)

    quantity_in_stock = models.IntegerField(default=0)
    autofill_quantity = models.IntegerField(default=0)
    avarage_unit_cost = models.IntegerField(default=0)
    pre_tax_retail_price = models.IntegerField(default=0)

    '''all_products model manager returns both all products including
    deactivated products i.e Products.all_products.all() returns both
    active and deactivated products use it when you need deactivate
    products as well.'''
    all_products = ProductManager(
        approved_only=False, active_only=False, original_only=False)
    objects = ProductManager(approved_only=False)

    class Meta:
        unique_together = ((
            "product_name",
            "manufacturer",
            "business",
            "description",
            "dispensing_size"))

    @property
    def get_tags(self):
        return self.tags.all()

    def __str__(self):
        return self.product_name

    def __repr__(self):
        return f"<{self.product_name}>"

    @property
    def product_batches(self):
        """
        get all the product batches associated with this product
        """
        from healthid.apps.orders.models.orders import ProductBatch
        return ProductBatch.objects.filter(
            product_id=self.id
        )

    def update_quantity_in_stock(self):
        """
        Reflect ProductBatches with the status 'IN_STOCK'
        """
        quantity_sum_dict = self.product_batches.filter(
            status="IN_STOCK",
        ).exclude(
            batch_ref="OUT OF STOCK"
        ).aggregate(quantity_sum=Sum('quantity'))

        quantity = quantity_sum_dict['quantity_sum'] or 0
        self.quantity_in_stock = quantity
        self.save()

    def pre_ordered_quantity(self):
        """
        Reflect ProductBatches with the status 'PENDING_DELIVERY'
        """
        quantity_sum_dict = self.product_batches.filter(
            status="PENDING_DELIVERY"
        ).aggregate(quantity_sum=Sum('quantity'))

        return quantity_sum_dict['quantity_sum'] or 0

    def update_autofill_quantity(self):
        suggest_quantity = self.reorder_max - (
                self.quantity_in_stock + self.pre_ordered_quantity())

        self.autofill_quantity = suggest_quantity if suggest_quantity > 0 else 0
        self.save()

    def update_avarage_unit_cost(self):
        available_batches = self.product_batches.filter(status="IN_STOCK")
        if available_batches.exists():
            result = available_batches.aggregate(models.Avg('unit_cost'))
        else:
            result = self.product_batches.aggregate(models.Avg('unit_cost'))

        self.avarage_unit_cost = result['unit_cost__avg'] or 0
        self.save()

    @staticmethod
    def pre_tax_retail_price_calculator(self):
        selling_price = self.sales_price or 0
        if self.product_batches.exists():
            if self.auto_price:
                selling_batch = self.product_batches.filter(
                    expiry_date__gte=datetime.datetime.now()
                ).order_by('-unit_cost').first()
                selling_price = selling_batch.unit_cost * \
                                Decimal(1 + self.markup / 100) \
                    if selling_batch else selling_price
            if not self.auto_price and self.sales_price is None:
                selling_price = Decimal(self.avarage_unit_cost) * \
                                Decimal(1 + self.markup / 100)

        selling_price = round_off_selling_price(selling_price)
        self.pre_tax_retail_price = selling_price

    def update_pre_tax_retail_price(self):
        Product.pre_tax_retail_price_calculator(self)
        self.save()

    @property
    def update_sales_price(self):
        selling_price = self.pre_tax_retail_price

        preference = self.business.outlet_set.first().outletpreference
        if self.vat_status:
            vat_rate = selling_price * Decimal(preference.vat_rate.rate)
            selling_price = int(selling_price) + int(vat_rate)

        selling_price = round_off_selling_price(selling_price)

        return selling_price

    def get_proposed_edit(self, request_id):
        proposed_edit = Product.all_products.filter(
            id=request_id, parent=self,
            is_approved=False, request_declined=False).first()
        if not proposed_edit:
            message = PRODUCTS_ERROR_RESPONSES[
                'wrong_proposed_edit_id'].format(self.product_name, request_id)
            raise ObjectDoesNotExist(message)
        return proposed_edit

    def approve_proposed_edit(self, request_id):
        proposed_edit = self.get_proposed_edit(request_id)

        product_dict = model_to_dict(proposed_edit)
        exclude_list = [
            'auto_price', 'parent', 'is_active', 'is_approved', 'sku_number',
            'user', 'business'
        ]
        [product_dict.pop(item) for item in exclude_list]
        product_dict['preferred_supplier_id'] = product_dict.pop(
            'preferred_supplier')
        product_dict['backup_supplier_id'] = product_dict.pop(
            'backup_supplier')
        product_dict['product_category_id'] = product_dict.pop(
            'product_category')
        product_dict['dispensing_size_id'] = product_dict.pop(
            'dispensing_size')
        product_dict.pop('id')
        for key, value in product_dict.items():
            if value is not None:
                setattr(self, key, value)
        proposed_edit.hard_delete()
        self.save()

    def decline_proposed_edit(self, request_id, comment):
        edit_request = self.get_proposed_edit(request_id)
        edit_request.admin_comment = comment
        edit_request.request_declined = True
        edit_request.save()
        return edit_request

    def get_batches(self, batch_ids):
        query = reduce(lambda q, id: q | Q(id=id), batch_ids, Q())
        product_batches = self.product_batches.filter(query)
        product_batch_ids = product_batches.values_list('id', flat=True)
        message = PRODUCTS_ERROR_RESPONSES['inexistent_batches']
        validator.check_validity_of_ids(
            batch_ids, product_batch_ids, message=message)
        return product_batches

    def update_inventory(self):
        """
        A singular function to update all the stock properties of a product
        """
        self.update_quantity_in_stock()
        self.update_autofill_quantity()
        self.update_avarage_unit_cost()
        self.update_pre_tax_retail_price()

    @staticmethod
    def general_search(search_term):
        search_filter = (
                Q(product_name__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(brand__icontains=search_term) |
                Q(manufacturer__icontains=search_term) |
                Q(product_category__name__icontains=search_term) |
                Q(preferred_supplier__name__icontains=search_term) |
                Q(sku_number__exact=search_term)
        )
        return search_filter


class ProductMeta(models.Model):
    """
    This model is for product meta data

    Attributes:
        dataKey(string): key of the value
        dataValue(string): Exact value of a key
        product: foreign key from product
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    dataKey = models.CharField(max_length=100, null=True)
    dataValue = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = (("product", "dataKey"))

    def __int__(self):
        return self.id


class BatchInfo(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    batch_no = models.CharField(
        max_length=100, null=True, blank=True, editable=False)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    date_received = models.DateField(auto_now=False)
    expiry_date = models.DateField(auto_now=False)
    unit_cost = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal('0.00'))
    sold_out = models.BooleanField(default=False)
    is_returnable = models.BooleanField(default=True)
    product = models.ForeignKey(
        Product, related_name='batch_info',
        on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_batches')
    service_quality = models.PositiveIntegerField(default=3)
    delivery_promptness = models.BooleanField(default=True)
    comment = models.TextField(blank=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.batch_no

    def __unicode__(self):
        return self.batch_no

    def save(self, *args, **kwargs):
        if not 1 <= self.service_quality <= 5:
            raise ValueError(PRODUCTS_ERROR_RESPONSES['invalid_batch_quality'])
        if Product.all_objects.filter(id=self.product_id).exists():
            if not self.product.is_approved:
                name = self.product.product_name
                message = PRODUCTS_ERROR_RESPONSES[
                    'unapproved_product_batch_error'].format(name)
                raise ObjectDoesNotExist(message)
        super(BatchInfo, self).save(*args, **kwargs)

    @property
    def quantity(self):
        """
        Property to return the total quantities of products
        in a batch.
        """
        original_quantity = Quantity.get_original_quantities(batch=self)
        return original_quantity.quantity_remaining if original_quantity else 0

    @property
    def proposed_quantity(self):
        """
        Property to return the total quantities of products
        in a batch.
        """
        proposed_quantity = Quantity.get_proposed_quantities(batch=self)
        return proposed_quantity.quantity_remaining if proposed_quantity else 0


class Quantity(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    batch = models.ForeignKey(
        BatchInfo, on_delete=models.CASCADE, related_name='batch_quantities')
    quantity_received = models.PositiveIntegerField(null=True, blank=True)
    quantity_remaining = models.PositiveIntegerField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    request_declined = models.BooleanField(default=False)
    proposed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='proposing_user',
        null=True, blank=True)
    authorized_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='approving_user',
        null=True, blank=True)
    comment = models.TextField(null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE,
                               related_name="proposedQuantityChange",
                               null=True, blank=True)

    objects = QuantityManager()
    all_quantities = QuantityManager(original_only=False)

    @staticmethod
    def get_proposed_quantities(batch=None):
        queryset = Quantity.all_quantities.filter(
            parent_id__isnull=False, request_declined=False, is_approved=False)
        if batch is not None:
            queryset = queryset.filter(batch=batch).first()
        return queryset

    @staticmethod
    def get_original_quantities(batch=None):
        queryset = Quantity.objects.all()
        if batch is not None:
            queryset = queryset.filter(batch=batch).first()
        return queryset


class Survey(BaseModel):
    """
    Model class for survey used to conduct supplier
    price checks for products.
    """
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    name = models.CharField(max_length=50, unique=True)
    outlet = models.ForeignKey(
        Outlet, on_delete=models.CASCADE, related_name='outlet_price_surveys')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_price_surveys')
    survey_closed = models.BooleanField(default=False)


class PriceCheckSurvey(BaseModel):
    """
    Model class for price check surveys.
    """
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_price_checks')
    supplier = models.ForeignKey(
        Suppliers, on_delete=models.CASCADE, related_name='supplier_prices')
    price = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal('0.00'))
    survey = models.ManyToManyField(Survey, related_name='survey_price_checks')
