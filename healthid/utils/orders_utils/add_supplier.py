import csv
from rest_framework.exceptions import NotFound, ValidationError

from healthid.apps.orders.models.suppliers import (
    Suppliers,
    SuppliersContacts,
    SuppliersMeta, Tier)
from healthid.apps.outlets.models import City, Country
from healthid.apps.authentication.models import User
from healthid.utils.app_utils.get_user_business import (
    get_user_business
)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.orders_utils.validate_suppliers_csv_upload import\
    validate_suppliers_csv_upload
from healthid.utils.get_on_duplication_csv_upload_actions import\
    get_on_duplication_csv_upload_actions
from healthid.utils.app_utils.generate_csv_file import generate_csv_file
from .suppliers_helper import upload_supplier_quickbook_csv_file
from healthid.apps.business.models import Business


class AddSupplier:
    def handle_csv_upload(self, user, io_string, on_duplication=''):
        """
        This CSV method loops through the csv file populating the DB with
        the information in the csv rows through the SaveContextManager,
        :param io_string:
        :return total number csv rows uploaded into the DB:
        """
        on_duplication_actions = get_on_duplication_csv_upload_actions(
            on_duplication)
        business = get_user_business(user)
        params = {'model': Suppliers, 'error_type': ValidationError}
        [supplier_count, row_count, error] = [0, 0, '']
        duplicated_suppliers = []
        suppliers = validate_suppliers_csv_upload(io_string)

        for row in suppliers:
            row_count += 1
            name = row.get('name')
            supplier = Suppliers.objects.filter(name__iexact=name)

            businesses = []

            for one_supplier in supplier:
                businesses.append(one_supplier.business.first())

            if supplier and business in businesses:
                duplicated_suppliers.append(
                    self.get_formated_duplicate_object(row_count, name, row))
            else:
                city = get_model_object(City,
                                        'name__iexact',
                                        row.get('city'),
                                        error_type=NotFound,
                                        label='name') \
                    if row.get('city') else None
                country = get_model_object(Country,
                                           'name__iexact',
                                           row.get('country'),
                                           error_type=NotFound,
                                           label='name') \
                    if row.get('country') else None
                tier = get_model_object(Tier,
                                        'name__iexact',
                                        row.get('tier'),
                                        error_type=NotFound,
                                        label='name') \
                    if row.get('tier') else None
                user_id = get_model_object(User,
                                           'id',
                                           user.pk,

                                           error_type=NotFound)
                try:
                    credit_days = int(row.get('credit days')) or 0
                except Exception:
                    credit_days = 0

                # validate payment terms
                if int(credit_days) > 0 and \
                        row.get('payment terms') == 'CASH_ON_DELIVERY':
                    error = ERROR_RESPONSES['payment_terms_cash_on_deliver']

                elif int(credit_days) <= 0 and \
                        row.get('payment terms') == 'ON_CREDIT':
                    error = ERROR_RESPONSES['payment_terms_on_credit']

                if error:
                    raise ValidationError(
                        {'error': f'{error} on row {row_count}'})
                if row.get('supplier_id'):
                    suppliers_instance = Suppliers(
                        name=name,
                        tier=tier,
                        user=user_id,
                        is_approved=True if row.get('is_approved') else False,
                        supplier_id=row.get('supplier_id')
                    )
                else:
                    suppliers_instance = Suppliers(
                        name=name,
                        tier=tier,
                        user=user_id,
                        is_approved=True if row.get('is_approved') else False,
                    )

                with SaveContextManager(suppliers_instance,
                                        **params) as supplier:
                    suppliers_instance.business.add(business)
                    suppliers_contacts_instance = \
                        SuppliersContacts(
                            email=row.get('email'),
                            mobile_number=row.get('mobile number'),
                            country=country,
                            address_line_1=row.get('address line 1'),
                            address_line_2=row.get('address line 2'),
                            lga=row.get('lga'),
                            city=city,
                            supplier_id=supplier.id
                        )

                    suppliers_meta_instance = SuppliersMeta(
                        display_name=f"{name} ({supplier.supplier_id})",
                        logo=row.get('logo'),
                        commentary=row.get('commentary'),
                        payment_terms=row.get('payment terms'),
                        credit_days=credit_days,
                        supplier_id=supplier.id
                    )
                    with SaveContextManager(
                            suppliers_meta_instance, model=SuppliersMeta):
                        pass

                    with SaveContextManager(suppliers_contacts_instance,
                                            model=SuppliersContacts):
                        pass

                    pass
                supplier_count += 1

        return {'supplier_count': supplier_count,
                'duplicated_suppliers': duplicated_suppliers}

    def retail_pro_suppliers(self, io_string, user, on_duplication):
        rows = []
        business = get_user_business(user)

        default_retai_pro = Suppliers.objects.get_or_create(
            user_id=user.id, name="RetailProVendor(default)", supplier_id="retail", tier_id=1, is_approved=True)

        if not default_retai_pro:
            default_retai_pro.business.add(business)

        for row in csv.DictReader(io_string):
            rows.append([
                (row.get('Vend Name') and row.get('Vend Name').replace(
                    '"', '').capitalize()) or 'N/A',
                (row.get('E-Mail') and row.get('E-Mail').replace('"', ''))
                or 'N/A',
                row.get('Phone1') or '+2359094444',
                user.active_outlet.business.country,
                (row.get('Addr1') and row.get('Addr1').replace(
                    '"', '').capitalize()) or 'N/A',
                (row.get('Addr2') and row.get('Addr2').replace(
                    '"', '').capitalize()) or 'N/A',
                (row.get('Addr3') and row.get('Addr3').replace(
                    '"', '').capitalize()) or 'N/A',
                user.active_outlet.business.city,
                row.get('Tier') or '3t+ wholesaler',
                'N/A',
                'N/A',
                'cash on delivery',
                0,
                True,
                row.get('Vendor Code'),
            ])
        header = [
            "Name",
            "Email",
            "Mobile Number",
            "country",
            "address line 1",
            "address line 2",
            "lga",
            "city",
            "tier",
            "logo",
            "commentary",
            "payment terms",
            "credit days",
            "is_approved",
            "supplier_id",
        ]
        custom_csv = generate_csv_file(header=header, rows=rows)
        return AddSupplier.handle_csv_upload(self,
                                             user, custom_csv, on_duplication)

    def quick_books_suppliers(self, io_string, user, on_duplication):
        rows = []
        business = get_user_business(user)

        default_quick_books_supplier = Suppliers.objects.get_or_create(
             user_id = user.id, name = "QuickBookVendor(default)", supplier_id = "quickbook", tier_id = 1, is_approved = True)
        if not default_quick_books_supplier:
            default_quick_books_supplier.business.add(business)


        for row in csv.DictReader(io_string):
            rows.append(upload_supplier_quickbook_csv_file(row, user))

        header = [
            "Name",
            "Email",
            "Mobile Number",
            "country",
            "address line 1",
            "address line 2",
            "lga",
            "city",
            "tier",
            "logo",
            "commentary",
            "payment terms",
            "credit days",
            'is_approved'
        ]
        custom_csv = generate_csv_file(header=header, rows=rows)
        return AddSupplier.handle_csv_upload(self,
                                             user, custom_csv, on_duplication)

    def get_formated_duplicate_object(self, row_count, name, row):
        return {
            'row': row_count,
            'message': ERROR_RESPONSES['duplication_error'].format(
                name),
            'data': row,
            'conflicts': Suppliers.objects.filter(
                name__iexact=name).values(
                'id', 'name', 'supplier_id')
        }
