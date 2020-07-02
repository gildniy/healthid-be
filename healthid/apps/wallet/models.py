from django.db import models
from healthid.models import BaseModel
from healthid.apps.profiles.models import Profile
from healthid.apps.authentication.models import User
from healthid.apps.preference.models import Currency


class CustomerCredit(BaseModel):
    """
        Customer credit account model
    """
    customer = models.OneToOneField(
        Profile, on_delete=models.SET_NULL, null=True, related_name="wallet")
    store_credit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    credit_currency = models.ForeignKey(
        Currency, on_delete=models.SET_NULL, null=True,
        related_name="currency")


class StoreCreditWalletHistory(BaseModel):
    """
    Increments or Decrements the store credit.
    """
    customer_account = models.ForeignKey(
        CustomerCredit, on_delete=models.SET_NULL, null=True,
        related_name='credit')
    sales_person = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='sell_by')
    credit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    debit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    current_store_credit = models.DecimalField(max_digits=10, decimal_places=2)
