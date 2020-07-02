from django.core.management import call_command

from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.suppliers import (
    approve_request,
    approve_supplier,
    approved_suppliers,
    decline_request,
    delete_supplier,
    edit_request,
    edit_request_two,
    edit_request_no_edit,
    edit_requests,
    edit_requests_paginated,
    edit_requests_paginated_two,
    edit_requests_paginated_three,
    edit_requests_wrong_argument,
    empty_search,
    filter_suppliers,
    filter_suppliers_paginated,
    invalid_search,
    supplier_mutation,
    user_requests,
    edit_proposal,
    all_suppliers_default_paginated,
    approved_suppliers_default_pagination_query,
    suppliers_notes_default_pagination,
    all_suppliers_custom_paginated,
    approved_suppliers_custom_pagination_query,
    suppliers_notes_custom_pagination,
    propose_edit_supplier)
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES
from healthid.tests.factories import SuppliersFactory, SupplierNoteFactory


class ManageSuppliersTestCase(BaseConfiguration):

    def setUp(self):
        super().setUp()
        call_command('loaddata', 'tests')
        self.supplier = self.query_with_token(
            self.access_token_master,
            supplier_mutation
        )
        self.supplier_id = \
            self.supplier['data']['addSupplier']['supplier']['id']
        self.approve_suppler = self.query_with_token(
            self.access_token_master,
            approve_supplier.format(
                supplier_id=self.supplier_id
            )
        )
        self.request = self.query_with_token(
            self.access_token_master,
            edit_request.format(
                supplier_id=self.supplier_id
            )
        )
        self.request_two = self.query_with_token(
            self.access_token_master,
            edit_request_two.format(
                supplier_id=self.supplier_id
            )
        )

        self.request_id = \
            self.request['data']['editSupplier']['editRequest']['id']
        self.request_two_id = \
            self.request_two['data']['editSupplier']['editRequest']['id']

    def test_approve_supplier(self):
        response = self.approve_suppler
        self.assertIn(
            'approved successfully!',
            response['data']['approveSupplier']['success'])

    def test_delete_supplier(self):
        response = self.query_with_token(
            self.access_token_master,
            delete_supplier.format(
                supplier_id=self.supplier_id
            )
        )
        self.assertIn(
            'deleted successfully!',
            response['data']['deleteSupplier']['success'])

    def test_propose_edit(self):
        response = self.request
        self.assertIn('sent!', response['data']['editSupplier']['message'])
        self.assertEqual(
            self.supplier_id,
            response['data']['editSupplier']['editRequest']['supplier']['id'])

    def test_propose_edit_no_edit(self):
        response = self.query_with_token(
            self.access_token_master,
            edit_request_no_edit.format(supplier_id=self.supplier_id)
        )
        self.assertIn(
            'No new information',
            response['errors'][0]['message'])

    def test_edit_proposal(self):
        response = self.query_with_token(
            self.access_token_master,
            edit_proposal.format(
                proposal_id=self.request_id)
        )
        self.assertIn('updated successfully!',
                      response['data']['editProposal']['message'])

    def test_edit_proposal_with_admin_from_another_business(self):

        response = self.query_with_token(
            self.login_third_master_admin_token,
            propose_edit_supplier.format(
                supplier_id=self.supplier_id, name="Andela Kigali")
        )
        self.assertIn(
            'You are not allowed to edit this supplier',
            response['errors'][0]['message'])

    def test_cannot_edit_request_you_didnot_propose(self):
        response = self.query_with_token(
            self.access_token,
            edit_proposal.format(
                proposal_id=self.request_id)
        )
        self.assertIn('did not propose!', response['errors'][0]['message'])

    def test_query_edit_requests(self):
        response = self.query_with_token(
            self.access_token_master,
            edit_requests
        )
        self.assertIsNotNone(response['data']['editSuppliersRequests'])

    def test_query_edit_requests_paginated(self):
        response = self.query_with_token(
            self.access_token_master,
            edit_requests_paginated
        )
        self.assertEqual(len(response['data']['editSuppliersRequests']), 1)
        self.assertEqual(response['data']['editSuppliersRequests'][0]['name'], 'shack')
        self.assertEqual(response['data']['totalSuppliersPagesCount'], 2)

    def test_query_edit_requests_paginated_two(self):
        response_two = self.query_with_token(
            self.access_token_master,
            edit_requests_paginated_two
        )
        self.assertEqual(len(response_two['data']['editSuppliersRequests']), 1)
        self.assertEqual(response_two['data']['editSuppliersRequests'][0]['name'], 'shacku')
        self.assertEqual(response_two['data']['totalSuppliersPagesCount'], 2)

    def test_query_edit_requests_paginated_three(self):
        response_three = self.query_with_token(
            self.access_token_master,
            edit_requests_paginated_three
        )
        self.assertEqual(len(response_three['data']['editSuppliersRequests']), 2)
        self.assertEqual(response_three['data']['editSuppliersRequests'][0]['name'], 'shack')
        self.assertEqual(response_three['data']['editSuppliersRequests'][1]['name'], 'shacku')
        self.assertEqual(response_three['data']['totalSuppliersPagesCount'], 1)

    def test_query_edit_requests_wrong_argument(self):
        response = self.query_with_token(
            self.access_token_master,
            edit_requests_wrong_argument
        )
        self.assertIsNotNone(response['errors'][0]['message'])

    def test_approve_edit_request(self):
        response = self.query_with_token(
            self.access_token_master,
            approve_request.format(
                request_id=self.request_id
            )
        )
        self.assertIn(
            'updated successfully!',
            response['data']['approveEditRequest']['message'])
        self.assertEqual(
            response['data']['approveEditRequest']['supplier']['id'],
            self.supplier_id)

    def test_approve_edit_request_inexistant(self):
        response = self.query_with_token(
            self.access_token_master,
            approve_request.format(
                request_id=self.request_id+"creed"
            )
        )
        self.assertIn(
            f"SupplierRevisions with id {self.request_id}creed does not exist",
            response['errors'][0]['message'])

    def test_decline_edit_request(self):
        response = self.query_with_token(
            self.access_token_master,
            decline_request.format(
                request_id=self.request_id
            )
        )
        self.assertIn(
            'declined!',
            response['data']['declineEditRequest']['message'])

    def test_query_approved_suppliers(self):
        response = self.query_with_token(
            self.access_token_master,
            approved_suppliers
        )
        self.assertIsNotNone(response['data']['approvedSuppliers'][0])

    def test_query_user_edit_requests(self):
        response = self.query_with_token(
            self.access_token,
            user_requests
        )
        self.assertEqual('Sport Direct', response['data']['userRequests'][0]['name'])

    def test_filter_supplier(self):
        response = self.query_with_token(
            self.access_token,
            filter_suppliers
        )
        self.assertEqual(
            'shadik.',
            response['data']['filterSuppliers']['edges'][0]['node']['name'])

    def test_filter_supplier_paginated(self):
        response = self.query_with_token(
            self.access_token,
            filter_suppliers_paginated
        )
        self.assertEqual(
            'shadik.',
            response['data']['filterSuppliers']['edges'][0]['node']['name'])
        self.assertEqual(
            1,len(response['data']['filterSuppliers']['edges']))

    def test_empty_search_result(self):
        response = self.query_with_token(
            self.access_token,
            empty_search
        )
        self.assertIn('does not exist!', response['errors'][0]['message'])

    def test_search_parameter(self):
        response = self.query_with_token(
            self.access_token,
            invalid_search
        )
        self.assertIn(ORDERS_ERROR_RESPONSES["supplier_search_key_error"],
                      response['errors'][0]['message'])

    def test_retrieve_all_suppliers_with_default_pagination(self):
        SuppliersFactory.create_batch(size=5)
        response = self.query_with_token(
            self.access_token_master,
            all_suppliers_default_paginated)
        self.assertEqual(response["data"]["totalSuppliersPagesCount"], 1)

    def test_retrieve_approved_suppliers_default_pagination(self):
        SuppliersFactory.create_batch(size=5, is_approved=True)
        response = self.query_with_token(
            self.access_token_master,
            approved_suppliers_default_pagination_query)
        self.assertEqual(response["data"]["totalSuppliersPagesCount"], 1)

    def test_retrieve_all_suppliers_notes_default_pagination(self):
        SupplierNoteFactory.create_batch(size=15)
        response = self.query_with_token(
            self.access_token_master,
            suppliers_notes_default_pagination)
        self.assertEqual(response["data"]["totalSuppliersPagesCount"], 1)

    def test_retrieve_all_suppliers_with_custom_pagination(self):
        SuppliersFactory.create_batch(size=13)
        response = self.query_with_token(
            self.access_token_master,
            all_suppliers_custom_paginated.format(pageCount=5, pageNumber=1))
        self.assertEqual(response["data"]["totalSuppliersPagesCount"], 1)

    def test_retrieve_approved_suppliers_custom_pagination(self):
        SuppliersFactory.create_batch(size=13, is_approved=True)
        response = self.query_with_token(
            self.access_token_master,
            approved_suppliers_custom_pagination_query.format(
                pageCount=5, pageNumber=1))
        self.assertEqual(response["data"]["totalSuppliersPagesCount"], 1)

    def test_retrieve_all_suppliers_notes_custom_pagination(self):
        SupplierNoteFactory.create_batch(size=13)
        response = self.query_with_token(
            self.access_token_master,
            suppliers_notes_custom_pagination.format(
                pageCount=5, pageNumber=1))
        self.assertEqual(response["data"]["totalSuppliersPagesCount"], 3)
