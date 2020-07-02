from django.db import models
from healthid.models import BaseModel
from healthid.apps.outlets.models import City, Country
from healthid.apps.business.models import Business


class BaseProfile(BaseModel):

    """A base profile model to hold common profile type fields."""

    CUSTOMER = 0
    USER_TYPES = (
        (CUSTOMER, "Customer"),)
    email = models.EmailField(
        max_length=100, null=True, default=None, blank=True)
    user_type = models.IntegerField(choices=USER_TYPES, default=CUSTOMER)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    primary_mobile_number = models.CharField(
        max_length=100, null=True, default=None, blank=True)
    secondary_mobile_number = models.CharField(max_length=100, null=True)
    address_line_1 = models.CharField(max_length=244, blank=True, null=True)
    address_line_2 = models.CharField(max_length=244, blank=True, null=True)
    local_government_area = models.CharField(max_length=244, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True


class CustomerProfile(models.Model):
    """
        Customer model
    """
    emergency_contact_name = models.CharField(max_length=200, null=True)
    emergency_contact_number = models.CharField(max_length=100, null=True)
    emergency_contact_email = models.EmailField(max_length=100, null=True)
    loyalty_member = models.BooleanField(default=False, null=True)
    loyalty_points = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        abstract = True


class Profile(CustomerProfile, BaseProfile):
    pass
