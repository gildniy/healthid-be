from django.db import models
from graphql.error import GraphQLError
from healthid.models import BaseModel
from healthid.utils.preference_utils.currency_fixture import MONEY_FORMATS
from healthid.apps.outlets.models import Outlet
from healthid.apps.business.models import Business
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.id_generator import ID_LENGTH, id_gen
from healthid.utils.app_utils.validator import validator
from healthid.utils.auth_utils.decorator import user_permission


class Timezone(BaseModel):
    name = models.CharField(max_length=244, unique=True)
    time_zone = models.CharField(
        max_length=244, unique=True)

    def __str__(self):
        return self.time_zone


class Currency(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    name = models.CharField(max_length=244, unique=True)
    symbol = models.CharField(max_length=244)
    symbol_native = models.CharField(max_length=244)
    decimal_digits = models.IntegerField()
    rounding = models.IntegerField()
    code = models.CharField(max_length=244, unique=True)
    name_plural = models.CharField(max_length=244)

    def __str__(self):
        return self.name

    money_formats = MONEY_FORMATS

    @classmethod
    def get_currency_formats(cls):
        """
        :rtype: list of all currency
        """
        return cls.money_formats


class Vat(BaseModel):
    # Model that handle VAT
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    rate = models.FloatField(default=00.00)


def update_vat(outlet_vat_rate, preference):
    if outlet_vat_rate <= 100 and outlet_vat_rate > 0:
        vat_id = preference.vat_rate.id
        vat = Vat.objects.get(pk=vat_id)
        vat.rate = outlet_vat_rate
        vat.save()
        return vat.rate
    else:
        raise GraphQLError(
            'Vat rate should not be more than 100 and it should be positive')


class Preference(BaseModel):
    """
    General model to preferences

    Attributes:
        email_preference: Choice if manager wants to receive email after order
        barcode_preference : Choice if outlet has a barcode scanning device
        reorder_point: minimum number of weeks for product stock to remain
        reorder_max = maximum number of weeks for stock to last
        retain_user = choice to retain operations user or log them out
        sales_hold = how long sales can be held for a customer
        sell_inventory_notification = notification preference for inventory
        payment_method = choice of payment method
        minimum_weeks_for_sales_velocity = how often velocity is calculated
        sales_velocity = sales velocity
        returnable_days = Choice for how long after sale a manager wants
        product to be returnable
    """
    email_preference = models.BooleanField(default=False)
    barcode_preference = models.BooleanField(default=False)
    reorder_point = models.IntegerField(default=3)
    reorder_max = models.IntegerField(default=6)
    retain_user = models.BooleanField(default=True)
    sales_hold = models.IntegerField(default=7)
    alert_low_inventory = models.BooleanField(default=False)
    alert_near_expiry = models.BooleanField(default=False)
    weeks_to_start_supply_alert = models.IntegerField(default=1)
    payment_method = models.CharField(default="all", max_length=50)
    minimum_weeks_for_sales_velocity = models.IntegerField(default=1)
    sales_velocity = models.IntegerField(default=1)
    returnable_days = models.IntegerField(default=30)

    class Meta:
        abstract = True

    def get_currency_from_file(self, name):
        # filters currency by name from the ist of currencies
        currencies = Currency.get_currency_formats()
        currency = Currency()
        default_currency = list(
            filter(lambda money: money['name'] == name, currencies))
        if default_currency:
            for(key, value) in default_currency[0].items():
                if key is not None:
                    setattr(currency, key, value)
            return currency
        raise GraphQLError(
            'Currency with name {} does not exist'.format(name))

    def get_currency(self, currency_name, **kwargs):
        # checks for currency in models before updating it.
        currencies = Currency.objects.filter(name=currency_name)
        if not currencies.exists():
            currency = self.get_currency_from_file(currency_name)
            for(key, value) in kwargs.items():
                if key is not None:
                    setattr(currency, key, value)
            currency.save()
            return currency
        return currencies.first()

    def update_preference(self, model, **kwargs):
        preference_id = kwargs.get('preference_id')
        payment_method = kwargs.get('payment_method')
        outlet_timezone_id = kwargs.get('outlet_timezone')
        outlet_currency = kwargs.get('outlet_currency')
        outlet_vat_rate = kwargs.get('outlet_vat')
        preference = get_model_object(model, 'id', preference_id)
        cash_methods = ('cash', 'card', 'bank_transfer', 'all', 'others', 'credit')
        outlet_preference_fields = (
            'outlet_timezone',
            'outlet_currency',
            'outlet_vat'
        )

        if outlet_vat_rate:
            if outlet_vat_rate > 100.00:
                raise GraphQLError("Vat rate cannot be greater than 100.0")
            outlet_vat = update_vat(outlet_vat_rate, preference)
            preference.vat_rate.rate = outlet_vat

        if outlet_timezone_id:
            outlet_timezone = get_model_object(
                Timezone, 'id', outlet_timezone_id)
            preference.outlet_timezone = outlet_timezone

        if outlet_currency:
            currency = self.get_currency(outlet_currency, **kwargs)
            preference.outlet_currency_id = currency.id

        if 'payment_method' in kwargs:
            payment_method = kwargs[
                "payment_method"] = payment_method.replace(' ', '')
            validator.validate_empty_field('Payment method', payment_method)

        if payment_method and payment_method not in cash_methods:
            raise GraphQLError('Invalid payment method option')

        for (key, value) in kwargs.items():
            if key and key in outlet_preference_fields:
                continue
            setattr(preference, key, value)
        preference.save()
        return preference


class OutletPreference(Preference):
    """
    General model for an outlet's preferences

    Attributes:
        outlet_id: preference settings belongs to this outlet
        outlet_timezone: Timezone for an outlet
        outlet_currency: Cuurrency unique to where outlet's location
        vat_rate: value added tax rate
    """
    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    outlet = models.OneToOneField(
        Outlet, on_delete=models.CASCADE, null=True)
    outlet_timezone = models.ForeignKey(
        Timezone, on_delete=models.CASCADE)
    outlet_currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    vat_rate = models.ForeignKey(Vat, on_delete=models.CASCADE)

    @user_permission('Manager')
    def update_preference(self, info, model, **kwargs):
        return super().update_preference(model, **kwargs)


class BusinessPreference(Preference):
    """
    General model for a business's preferences

    Attributes:
        business_id: Business that owns preference settings
    """
    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    business = models.OneToOneField(
        Business, on_delete=models.CASCADE)
