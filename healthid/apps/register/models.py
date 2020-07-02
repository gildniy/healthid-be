from django.db import models

from healthid.models import BaseModel
from healthid.apps.outlets.models import Outlet
from healthid.apps.receipts.models import ReceiptTemplate


class Register(BaseModel):
    name = models.CharField(max_length=244)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE,
                               related_name='outlet_register')
    register_id = models.CharField(max_length=244, null=True)
    original_name = models.CharField(max_length=244)
    original_objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
