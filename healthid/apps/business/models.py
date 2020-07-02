from django.db import models

from healthid.apps.authentication.models import User
from healthid.models import BaseModel
from healthid.utils.app_utils.id_generator import id_gen


class Business(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    trading_name = models.CharField(max_length=244)
    legal_name = models.CharField(max_length=244, unique=True)
    address_line_1 = models.CharField(max_length=244, blank=True)
    address_line_2 = models.CharField(max_length=244, blank=True)
    local_government_area = models.CharField(max_length=244, blank=True)
    country = models.CharField(max_length=244, blank=True)
    city = models.CharField(max_length=244, blank=True)
    phone_number = models.CharField(max_length=25)
    business_email = models.EmailField(blank=True, unique=True)
    website = models.CharField(max_length=344)
    facebook = models.CharField(max_length=344)
    twitter = models.CharField(max_length=344)
    instagram = models.CharField(max_length=244)
    logo = models.URLField()
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="business_user",
        null=True
    )

    def __str__(self):
        return self.legal_name


class UserBusiness(models.Model):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    business = models.ForeignKey(
        Business, related_name='users', on_delete=models.CASCADE)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_business",
        null=True
    )
