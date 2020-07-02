from django.core import mail
from django.test import TestCase
from healthid.tests.factories import (OrderFactory, OrderDetailsFactory,
                                      SupplierOrderDetailsFactory,
                                      SuppliersContactsFactory,
                                      SuppliersFactory, OutletFactory,
                                      OutletKindFactory, CityFactory,
                                      CountryFactory, BusinessFactory,
                                      UserFactory, TimezoneFactory)

from healthid.apps.orders.services import (SupplierOrderDetailsFetcher,
                                           SupplierOrderEmailSender,
                                           SupplierOrderDetailsApprovalService)


class TestSupplierOrders(TestCase):

    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()

        self.timezone1 = TimezoneFactory()
        self.country1 = CountryFactory()

        self.city1 = CityFactory(country=self.country1)

        self.business = BusinessFactory.create(user=(self.user1,))

        self.outlet_kind = OutletKindFactory()
        self.outlet = OutletFactory.create(kind=self.outlet_kind)

        self.order1 = OrderFactory()
        self.order_details2 = OrderDetailsFactory(order=self.order1)
        self.order_details2 = OrderDetailsFactory(order=self.order1)

        self.supplier = SuppliersFactory(user=self.user2)
        self.supplier_contacts = SuppliersContactsFactory(
            supplier=self.supplier)

        self.supplier_order1 = SupplierOrderDetailsFactory(
            order=self.order1, supplier=self.supplier)
        self.supplier_order2 = SupplierOrderDetailsFactory(
            order=self.order1, supplier=self.supplier)

    def test_fetch_supplier_details(self):
        """Test """
        supplier_orders = [self.supplier_order2, self.supplier_order1]
        supplier_order_ids = [s.id for s in supplier_orders]
        fetcher = SupplierOrderDetailsFetcher(self.order1.id,
                                              supplier_order_ids)
        self.assertEqual(supplier_orders,
                         list(fetcher.fetch()))

    def test_approve_supplier_order_details(self):
        supplier_order1 = SupplierOrderDetailsFactory(order=self.order1,
                                                      supplier=self.supplier)
        supplier_order2 = SupplierOrderDetailsFactory(order=self.order1,
                                                      supplier=self.supplier)
        supplier_orders = [supplier_order2, supplier_order1]
        approval_service = SupplierOrderDetailsApprovalService(
            supplier_orders, self.user1, "blah blah")
        approval_service.approve()
        self.assertTrue(supplier_order1.approved)
        self.assertTrue(supplier_order2.approved)
        self.assertEqual(supplier_order2.approved_by, self.user1)
        self.assertEqual(supplier_order1.approved_by, self.user1)

    def test_sending_supplier_order_emails(self):
        supplier_order1 = SupplierOrderDetailsFactory(order=self.order1,
                                                      supplier=self.supplier)
        supplier_order2 = SupplierOrderDetailsFactory(order=self.order1,
                                                      supplier=self.supplier)
        supplier_orders = [supplier_order1, supplier_order2]
        email_sender = SupplierOrderEmailSender(supplier_orders)
        email_sender.send()
        self.assertEqual(len(mail.outbox), 2)
