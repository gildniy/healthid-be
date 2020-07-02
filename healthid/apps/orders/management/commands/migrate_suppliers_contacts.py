from django.core.management.base import BaseCommand
from healthid.apps.orders.models.suppliers import SuppliersContacts, SupplierOutletContacts
from healthid.apps.orders.models.suppliers import Business
from healthid.apps.outlets.models import Outlet

class Command(BaseCommand):
    args = 'No Arguments'
    help = 'Migrate suppliers contacts'

    def _migrate_suppliers_contacts(self):
        supplier_contacts = SuppliersContacts.objects.defer("outlet")
        outlet_supplier_contacts = []
        for contact in supplier_contacts:
            supplier = contact.supplier
            for business in supplier.business.all():
                outlets = Outlet.objects.filter(business_id=business.id)
                outlet_supplier_contacts.append((supplier, outlets, contact))

        for outlet_supplier_contact in outlet_supplier_contacts:
            contact = outlet_supplier_contact[2]
            supplier = outlet_supplier_contact[0]
            for outlet in outlet_supplier_contact[1]:
                data_keys = ["email", "mobile_number", "address_line_1", "address_line_2", "lga", "city_id", "country_id"]
                for key in data_keys:
                    SupplierOutletContacts.objects.create(
                        dataKey=key, dataValue=getattr(contact, key), outlet=outlet, supplier=supplier
                    )
                

    def handle(self, *args, **options):
        self._migrate_suppliers_contacts()

