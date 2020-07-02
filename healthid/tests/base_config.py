import json
from datetime import datetime

from django.forms import model_to_dict
from django.test import Client, TestCase

from healthid.apps.authentication.models import Role, User
from healthid.apps.events.models import Event, EventType
from healthid.apps.orders.models import (Order, SupplierNote,
                                         Suppliers, SuppliersContacts,
                                         SuppliersMeta, Tier)
from healthid.apps.outlets.models import (
    City, Country, Outlet, OutletKind, OutletUser)
from healthid.apps.products.models import (BatchInfo, DispensingSize, Product,
                                           ProductCategory, Quantity)
from healthid.apps.profiles.models import Profile
from healthid.apps.sales.models import SalesPrompt
from healthid.apps.stock.models import StockCountTemplate
from healthid.apps.preference.models import (Timezone,
                                             OutletPreference, Currency)
from healthid.tests.test_fixtures.authentication import login_user_query
from healthid.utils.business_utils.create_business import create_business, create_business2
from healthid.apps.receipts.models import ReceiptTemplate
from healthid.apps.consultation.models import CustomerConsultation
from healthid.apps.notifications.models import Notification, NotificationMeta
from healthid.apps.business.models import UserBusiness


class BaseConfiguration(TestCase):
    """
    Base configuration file for all tests.
    """

    @classmethod
    def setUpClass(cls):

        # We need to first run setUpClass function that we
        # inherited from TestCase.
        super(BaseConfiguration, cls).setUpClass()

        # Set up test client for all test classes
        # that will inherit from this class.
        cls.client = Client()

    @classmethod
    def query(cls, query: str = None):
        # Method to run all queries and mutations for tests.
        body = dict()
        body['query'] = query
        response = cls.client.post(
            '/healthid/', json.dumps(body), content_type='application/json')
        json_response = json.loads(response.content.decode())
        return json_response

    @classmethod
    def query_with_token(cls, access_token, query: str = None):
        # Method to run queries and mutations using a logged in user
        # with an authentication token
        body = dict()
        body['query'] = query
        http_auth = 'JWT {}'.format(access_token)
        url = '/healthid/'
        content_type = 'application/json'

        response = cls.client.post(
            url,
            json.dumps(body),
            HTTP_AUTHORIZATION=http_auth,
            content_type=content_type)
        json_response = json.loads(response.content.decode())
        return json_response

    def setUp(self):
        """
        Configurations to be made available before each
        individual test case inheriting from this class.
        """
        self.new_user = {
            "email": "john.doe@gmail.com",
            "mobile_number": "+256770777777",
            "password": "Password123"
        }
        self.invalid_email_user = {
            "email": "john.dogmail.com",
            "mobile_number": "+256770777777",
            "password": "Password123"
        }
        self.invalid_mobile_user = {
            "email": "john.edo@gmail.com",
            "mobile_number": "0777777",
            "password": "Password123"
        }
        self.new_manager = {
            "email": "ephraim@gmail.com",
            "mobile_number": "+256770777000",
            "password": "Password123"
        }
        self.stock_count_user1 = {
            "email": "arkafuuma@gmail.com",
            "mobile_number": "+256470777777",
            "password": "Password123"
        }
        self.stock_count_user2 = {
            "email": "arkafuuma2@gmail.com",
            "mobile_number": "+256570777777",
            "password": "Password123"
        }
        self.master_admin = {
            "email": "you@example.com",
            "mobile_number": "+256770777797",
            "password": "Password123"
        }
        self.another_master_admin = {
            "email": "for@example.com",
            "mobile_number": "+256770777799",
            "password": "Password123"
        }

        self.second_master_admin = {
            "email": "you.second@example.com",
            "mobile_number": "+256770777798",
            "password": "Password1234"
        }

        self.login_second_master_admin = {
            "email": "you.second@example.com",
            "password": "Password1234"
        }

        self.third_master_admin = {
            "email": "third.master@example.com",
            "mobile_number": "+256270772798",
            "password": "Password1234"
        }

        self.login_third_master_admin = {
            "email": "third.master@example.com",
            "password": "Password1234"
        }

        self.login_user = {
            "email": "john.doe@gmail.com",
            "password": "Password123"
        }
        self.login_master_admin = {
            "email": "you@example.com",
            "password": "Password123"
        }
        self.login_another_master_admin = {
            "email": "for@example.com",
            "password": "Password123"
        }
        self.update_user_data = {
            'firstname': 'kafuuma',
            'lastname': 'henry',
            'username': 'kafuumahenry',
            'email': 'healthid@gmail.com',
            'secondary_email': 'healthid@gmail.com',
            'mobile_number': '+254786299914',
            'secondary_phone_number': "+254786299914"
        }
        self.outlet = {
            'name': 'bingo',
            'address_line1': "wandegya",
            'phone_number': "+254745345342",
            'address_line2': "Central, Kla",
            'lga': "KCCA",
            'date_launched': "1995-10-20"
        }
        self.second_outlet = {
            'name': 'bingow',
            'address_line1': "wandegya ku bitaala",
            'phone_number': "+254745345341",
            'address_line2': "Central, Kla",
            'lga': "KCCA",
            'date_launched': "1995-10-20"
        }

        self.role = self.create_role(role_name="Cashier")
        self.manager_role = self.create_role(role_name="Manager")
        self.master_admin_role = self.create_role('Master Admin')
        self.business = create_business()
        self.business2 = create_business2()
        self.user = self.register_user(self.new_user, self.business)
        self.manager = self.register_manager(self.new_manager)
        self.outlet_kind = self.create_outlet_kind()
        self.supplier = self.create_suppliers(self.user)
        self.supplier_contacts = self.create_suppliers_contacts(self.supplier)
        self.supplier_meta = self.create_suppliers_meta(self.supplier)
        self.timezone = Timezone(
            id="285461788", name="Africa/Lagos", time_zone="(GMT+01:00) Lagos")
        self.timezone.save()
        self.outlet = self.create_outlet(self.outlet)
        self.user_outlet = self.create_user_outlet(self.user, self.outlet)
        self.dispensing_size = self.create_dispensing_size()
        self.product_category = self.create_product_category(self.business)
        self.product = self.create_product()
        self.batch_info = self.create_batch_info()
        self.sales_prompt = self.create_sales_prompt()
        self.suppliers_note = self.create_suppliers_note()
        self.event = self.create_event()
        self.order = self.create_order()
      
        OutletUser.objects.create(
            user=self.user, outlet=self.outlet, is_active_outlet=True)
        OutletUser.objects.create(
            user=self.manager, outlet=self.outlet, is_active_outlet=True)

        # register and log in user
        self.access_token = self.user_login()
        self.master_admin_user = self.register_master_admin(self.master_admin, self.business)
        self.business.user = self.master_admin_user
        self.business.save()

        self.another_master_admin_user = self.register_master_admin(
            self.another_master_admin, self.business)
        self.second_master_admin_user = self.register_master_admin(
            self.second_master_admin, self.business)
        self.third_master_admin_user = self.register_master_admin(self.third_master_admin,self.business2)
        self.second_master_admin_token = self.admin_login(
            self.login_second_master_admin)
        self.access_token_master = self.admin_login(self.login_master_admin)
        self.another_master_admin_token = self.admin_login(
            self.login_another_master_admin)
        self.login_third_master_admin_token = self.admin_login(self.login_third_master_admin)
        self.preference = OutletPreference.objects.filter().first()
        self.currency = Currency.objects.filter(
            id=self.preference.outlet_currency_id).first()
        self.second_outlet = self.create_outlet(self.second_outlet)

        OutletUser.objects.create(user=self.second_master_admin_user,
                                  outlet=self.second_outlet,
                                  is_active_outlet=True)
        OutletUser.objects.create(user=self.master_admin_user,
                                  outlet=self.outlet,
                                  is_active_outlet=True)

        self.notification = self.create_notification(
            self.user, 'general_notification', 'subject')

        self.create_customer_data = {
            "first_name": "Habib",
            "last_name": "Audu",
            "email": "talktohabib@gmail.com",
            "city_id": self.outlet_kind['city_id'],
            "country_id": self.outlet_kind['country_id'],
            "primary_mobile_number": "+256788088831",
            "secondary_mobile_number": "+256788088831",
            "loyalty_member": "true",
            "emergency_contact_email": "talktohabi2@gmail.com"
        }

        self.customer_1 = self.create_customer({
            "first_name": "Dany",
            "last_name": "Stomborn",
            "email": "dany.stomborn@got.com",
            "city_id": self.outlet_kind['city_id'],
            "country_id": self.outlet_kind['country_id'],
            "primary_mobile_number": "+234788088831",
            "secondary_mobile_number": "+234788088832",
            "loyalty_member": True,
            "local_government_area": "Heming way",
            "address_line_1": "20, king's Landing",
            "address_line_2": "Esos lane",
            "emergency_contact_name": "Frodo",
            "emergency_contact_email": "saruman@lotr.world",
            "emergency_contact_number": "+234897090878 "
        })

        self.invoice_data = {
            "outlet_id": self.outlet.id,
            "order_id": self.order.id,
            "image_url": "http://onlineblueprintprinting.com/wp-content/"
            "uploads/free-editable-invoice-template-invoice-template-"
            "free-and-fully-customizable-online-templates.png",
        }

    def assertResponseNoErrors(self, resp: dict, expected: dict):
        self.assertNotIn("errors", resp, "Response had errors")
        self.assertEqual(resp["data"], expected, "Response has correct data")

    def register_user(self, user, business):
        """
        register a new user
        """
        email = user["email"]
        mobile_number = user["mobile_number"]
        password = user["password"]
        user = User.objects.create_user(
            email=email, mobile_number=mobile_number, password=password)
        user.is_active = True
        user.save()
        business_user = UserBusiness(business=business, user=user)
        business_user.save()
        return user

    def register_manager(self, user):
        """
        register a new user
        """
        email = user["email"]
        mobile_number = user["mobile_number"]
        password = user["password"]
        user = User.objects.create_user(
            email=email, mobile_number=mobile_number, password=password)
        user.is_active = True
        user.role = self.manager_role
        user.save()
        return user

    def register_master_admin(self, master_admin, business):
        """
        register a master admin
        """
        email = master_admin["email"]
        mobile_number = master_admin["mobile_number"]
        password = master_admin["password"]
        user = User.objects.create_user(
            email=email, mobile_number=mobile_number, password=password)
        user.is_active = True
        user.role = self.master_admin_role
        user.save()
        business_user = UserBusiness(business=business, user=user)
        business_user.save()
        return user

    def user_login(self):
        """
        Log in registered user and return a token
        """
        response = self.query(login_user_query.format(**self.login_user))
        return response['data']['tokenAuth']['token']

    def admin_login(self, admin):
        """
        Log in registered user and return a token
        """
        response = self.query(
            login_user_query.format(**admin))
        return response['data']['tokenAuth']['token']

    def create_outlet_kind(self):
        country = Country.objects.create(name='Peru')
        city = City.objects.create(name="Chiclayo", country_id=country.id)
        outlet_kind = OutletKind.objects.create(name="Warehouse")
        info = {"city_id": city.id, "outlet_kindid": outlet_kind.id,
                "country_id": country.id}
        return info

    def create_outlet(self, outlet):
        info = self.outlet_kind
        return Outlet.objects.create(
            name=outlet["name"],
            kind_id=info["outlet_kindid"],
            business_id=self.business.id)

    def create_user_outlet(self, user, outlet):
        return OutletUser.objects.create(
            user=user, outlet=outlet, is_active_outlet=True)

    def create_order(self, closed=True):
        """Return an instance of Order.

        If closed is True return a closed order

        Args:
            closed (Bool): order closed flag

        Returns:
            order (:obj) `model`
        """
        return Order.objects.create(
            order_number="5757575",
            name="ututu",
            product_autofill=True,
            supplier_autofill=True,
            delivery_date="2012-12-12",
            sent_status=True,
            destination_outlet_id=self.outlet.id,
            closed=closed,
            user=self.user
        )

    def create_role(self, role_name):
        return Role.objects.create(name=role_name)

    def create_suppliers(self, user):
        tier = Tier.objects.create(name="exporter")
        supplier = Suppliers.objects.create(
            name='Sport Direct',
            tier=tier,
            user=user,
            is_approved=True)
        supplier.business.add(self.business)
        return supplier

    def create_suppliers_contacts(self, supplier):
        city = City.objects.get(name="Chiclayo")
        country = Country.objects.get(name="Peru")

        return SuppliersContacts.objects.create(
            email='sportdirect@mail.com',
            mobile_number='+254745345342',
            address_line_1="address line 1",
            address_line_2="address line 2",
            city=city,
            country=country,
            supplier=supplier)

    def create_suppliers_meta(self, supplier):

        return SuppliersMeta.objects.create(
            credit_days=10,
            logo='image.png',
            payment_terms='ON_CREDIT',
            commentary='good supplier',
            supplier=supplier)

    def create_dispensing_size(self):
        return DispensingSize.objects.create(name='kilogram')

    def create_product_category(self, business):
        return ProductCategory.objects.create(name='Prescription',
                                              business=business)

    def create_product(self, product_name='Pizza'):
        return Product.objects.create(
            product_name=product_name,
            sales_price=100,
            product_category=self.product_category,
            dispensing_size=self.dispensing_size,
            preferred_supplier=self.supplier,
            backup_supplier=self.supplier,
            business=self.business,
            is_approved=True)

    def create_batch_info(self):
        batch_info = BatchInfo.objects.create(
            supplier=self.supplier,
            product=self.product,
            user=self.user,
            date_received='2019-01-03',
            expiry_date='2019-03-03'
        )
        Quantity.objects.create(
            batch=batch_info, quantity_received=8, quantity_remaining=8,
            is_approved=True)
        batch_info.save()
        return batch_info

    def create_sales_prompt(self):
        return SalesPrompt.objects.create(
            prompt_title="Title for Sales Prompt",
            description="Sales Prompt Description",
            product=self.product,
            outlet=self.outlet
        )

    def create_event(
        self, event_title='some event',
        description='urgent event',
    ):
        event_type = EventType.objects.create(name='Outlet Event')
        event = Event.objects.create(
            event_title=event_title, start_date=datetime.now(),
            end_date=datetime.now(), description=description,
            event_type=event_type, start_time=datetime.now(),
            end_time=datetime.now(),
        )
        event.user.add(self.user)
        return event

    def create_stock_template(self):
        stock_template = StockCountTemplate.objects.create(
            outlet=self.outlet,
            schedule_time=self.event
        )
        stock_template.products.add(self.product)
        stock_template.assigned_users.add(self.user)
        stock_template.designated_users.add(self.user)
        stock_template.save()
        return stock_template

    def create_suppliers_note(self):
        supplier = SupplierNote.objects.create(
            supplier=self.supplier,
            user=self.user,
            note="Amazing supplier"
        )
        supplier.outlet.add(self.outlet)
        return supplier

    @staticmethod
    def create_customer(data):
        return Profile.objects.create(**data)

    @staticmethod
    def customer_fields_to_dict(data):
        customer_data = model_to_dict(data)
        customer_data["city_id"] = customer_data.pop("city")
        customer_data["country_id"] = customer_data.pop("country")
        customer_data["loyalty_member"] = str(
            customer_data["loyalty_member"]).lower()
        return customer_data

    def create_receipt_template(self):
        return ReceiptTemplate.objects.create(outlet=self.outlet)

    def schedule_consultation(self):
        consultation = CustomerConsultation.objects.create(
            outlet=self.outlet,
            event=self.event,
            booked_by=self.user,
            customer=self.customer_1

        )
        return consultation

    def create_notification(self, user, event_name, subject):
        notification = Notification.objects.create(subject=subject,
                                                   user=user,
                                                   event_name=event_name or
                                                   Notification().event_name)
        notification_meta = NotificationMeta.objects.create(
            notification=notification,
            body='body')

        notification.notification_meta = notification_meta

        return notification
