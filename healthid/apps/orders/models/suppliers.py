from django.db import models
from django.contrib.postgres.fields import JSONField

from healthid.apps.authentication.models import User
from healthid.apps.business.models import Business
from healthid.apps.outlets.models import Outlet, Country, City
from healthid.models import BaseModel
from healthid.utils.app_utils.id_generator import id_gen
from healthid.apps.orders.enums.suppliers import PaymentTermsType
from healthid.utils.app_utils.database import get_model_object


class Tier(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class PaymentTerms(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Suppliers(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    name = models.CharField(max_length=100)
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    supplier_id = models.CharField(max_length=25, null=False)
    is_approved = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='supplier_creator')
    business = models.ManyToManyField('business.Business')

    def __str__(self):
        return self.name

    @property
    def get_supplier_contacts(self):
        """
        get contacts of a supplier

        Returns:
            list: contacts of a single supplier
        """
        contacts_list = SupplierOutletContacts.objects.all().filter(
            supplier=self.id).values('supplier_id', 'outlet_id', 'dataKey', 'dataValue')
        outlets_list = SupplierOutletContacts.objects.distinct('outlet_id').filter(
            supplier=self.id).values('outlet_id')
 
        contact_items = []
        for outlet in outlets_list:
            outlet = outlet['outlet_id']
            contact_item = {}
            for contact in contacts_list:
                if contact['outlet_id'] == outlet:
                    contact_item[contact['dataKey']] = contact['dataValue']
            contact_item['outlet_id'] = outlet
            contact_items.append(contact_item)
            contact_item = {}

        return contact_items


    @property
    def get_supplier_meta(self):
        """
        get meta data of a supplier

        Returns:
            list: meta data of a single supplier
        """
        return SuppliersMeta.objects.all().filter(
            supplier=self.id, edit_request_id=None)

class SupplierRevisions(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    version = JSONField()
    proposed_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="edit_creator")
    status = models.CharField(max_length=8, default="inactive")
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="approved_by", null=True)

    def __str__(self):
        return f"{self.supplier}-{self.created_at}-{self.proposed_by}"

class SuppliersContacts(BaseModel):
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    email = models.EmailField(max_length=100, null=True)
    mobile_number = models.CharField(max_length=100, null=True)
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    lga = models.CharField(max_length=255, null=True)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    edit_request_id = models.CharField(max_length=255, null=True)

    class Meta:
       managed = False

class SupplierOutletContacts(BaseModel):
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    dataKey = models.CharField(max_length=255, null=True)
    dataValue = models.CharField(max_length=255, null=True)

    class Meta:
         unique_together = (("supplier", "outlet", "dataKey"))

class SuppliersMeta(BaseModel):
    display_name = models.CharField(max_length=100, null=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    logo = models.URLField(null=True)
    payment_terms = models.CharField(
        max_length=100, choices=PaymentTermsType.choices(), null=True)
    credit_days = models.IntegerField(null=True)
    commentary = models.TextField(null=True)
    admin_comment = models.TextField(null=True)
    edit_request_id = models.CharField(max_length=255, null=True)

class SupplierNote(BaseModel):
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    outlet = models.ManyToManyField(Outlet, related_name='supplier_note')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='note_creator')
    note = models.TextField(default="user note about this supplier")


class SupplierRating(BaseModel):
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    rating = models.IntegerField(null=False, default=0)
