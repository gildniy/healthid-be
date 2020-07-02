from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.suppliers import (
    create_suppliers_note,
    update_suppliers_note,
    delete_supplier_note,
    all_suppliers_note,
    supplier_notes)
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES
from healthid.utils.messages.outlet_responses import OUTLET_ERROR_RESPONSES
from healthid.utils.messages.common_responses import (
    SUCCESS_RESPONSES, ERROR_RESPONSES)
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES
from healthid.tests.factories import SupplierNoteFactory


class TestSuppliersNote(BaseConfiguration):
    def setUp(self):
        super(TestSuppliersNote, self).setUp()
        self.supplier_note_factory = SupplierNoteFactory(
            user=self.master_admin_user)

    def test_create_suppliers_note(self):
        """Test method for creating a suppliers note"""
        data = {
            "supplier_id": self.supplier.id,
            "outlet_id": self.outlet.id,
            "note": "Great Supplier man"
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = SUCCESS_RESPONSES[
            "creation_success"].format("Supplier's note")
        self.assertEqual(
            expected_message,
            response["data"]["createSuppliernote"]["message"])
        self.assertNotIn("errors", response)

    def test_create_suppliers_note_with_invalid_supplier_id(self):
        """Test method for creating a suppliers note with invalid input"""
        data = {
            "supplier_id": 0,
            "outlet_id": self.outlet.id,
            "note": "Great Supplier"
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = PRODUCTS_ERROR_RESPONSES[
            "inexistent_supplier"].format("0")
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_suppliers_note_with_special_characters(self):
        """Test method for creating a suppliers note with special characters"""
        data = {
            "supplier_id": self.supplier.id,
            "outlet_id": self.outlet.id,
            "note": "Great <>]]]#@ Supplier"
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = "Special characters not allowed"
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_suppliers_note_with_less_than_two_words(self):
        """
          Test method for creating a suppliers note with less than two words
        """
        data = {
            "supplier_id": self.supplier.id,
            "outlet_id": self.outlet.id,
            "note": "Great "
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = ORDERS_ERROR_RESPONSES["supplier_note_length_error"]
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_suppliers_note_with_invalid_outlet_id(self):
        """Test method for creating a suppliers note with invalid input"""
        supplier_note = SupplierNoteFactory(note="His delivery was timely")
        note = supplier_note.note
        data = {
            "supplier_id": self.supplier.id,
            "outlet_id": 300,
            "note": note
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = OUTLET_ERROR_RESPONSES[
            "inexistent_outlet"].format("300")
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_create_suppliers_note_with_invalid_zero_outlet_id(self):
        """Test method for creating a suppliers note with invalid zero input"""
        supplier_note = SupplierNoteFactory(note="His delivery was timely")
        note = supplier_note.note
        data = {
            "supplier_id": self.supplier.id,
            "outlet_id": 0,
            "note": note
        }
        response = self.query_with_token(
            self.access_token,
            create_suppliers_note.format(**data))
        expected_message = ERROR_RESPONSES['invalid_id'
                                           ].format('0')
        self.assertEqual(
            expected_message,
            response['errors'][0]['message'])

    def test_update_suppliers_note(self):
        """Test method for updating a suppliers note"""
        data = {
            "supplier_note": self.supplier_note_factory.id,
            "outlet_id": self.outlet.id,
            "note": "Update Supplier note"
        }
        response = self.query_with_token(
            self.access_token_master,
            update_suppliers_note.format(**data))
        expected_message = SUCCESS_RESPONSES[
            "update_success"].format("Supplier's note")
        self.assertEqual(
            expected_message,
            response["data"]["updateSuppliernote"]["success"])
        self.assertNotIn("errors", response)

    def test_update_suppliers_note_with_less_than_two_words(self):
        """
          Test method for updating a suppliers note, with less than two words
        """
        data = {
            "supplier_note": self.supplier_note_factory.id,
            "outlet_id": self.outlet.id,
            "note": "Updated  "
        }
        response = self.query_with_token(
            self.access_token_master,
            update_suppliers_note.format(**data))
        expected_message = ORDERS_ERROR_RESPONSES["supplier_note_length_error"]
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_update_suppliers_note_with_special_characters(self):
        """
          Test method for updating a suppliers note, with special characters
        """
        data = {
            "supplier_note": self.supplier_note_factory.id,
            "outlet_id": self.outlet.id,
            "note": "Updated %^&$3$@ suplier "
        }
        response = self.query_with_token(
            self.access_token_master,
            update_suppliers_note.format(**data))
        expected_message = "special characters not allowed"
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_update_suppliers_note_with_invalid_user(self):
        """
          Test method for updating a suppliers note, with invalid user
        """
        data = {
            "supplier_note": self.suppliers_note.id,
            "outlet_id": self.outlet.id,
            "note": "Updating supplier "
        }
        response = self.query_with_token(
            self.access_token_master,
            update_suppliers_note.format(**data))
        expected_message = ORDERS_ERROR_RESPONSES[
            "supplier_note_update_validation_error"]
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_get_all_suppliers_note(self):
        """Test method for quering all suppliers note"""
        response = self.query_with_token(
            self.access_token,
            all_suppliers_note)
        self.assertIn("allSuppliersNote", response["data"])
        self.assertNotIn("errors", response)

    def test_get_a_suppliers_notes(self):
        """Test method for quering a particular suppliers note"""
        response = self.query_with_token(
            self.access_token,
            supplier_notes(self.suppliers_note.supplier_id))
        self.assertIn("suppliersNote", response["data"])
        self.assertNotIn("errors", response)

    def test_get_a_suppliers_notes_with_invalid_supplier_id(self):
        """
         Test method for quering a particular suppliers note with invalid id
        """
        response = self.query_with_token(
            self.access_token,
            supplier_notes(0))
        expected_message = PRODUCTS_ERROR_RESPONSES[
            "inexistent_supplier"].format("0")
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_delete_suppliers_note_with_invalid_user(self):
        """Test method for deleting suppliers note with invalid user"""
        response = self.query_with_token(
            self.access_token_master,
            delete_supplier_note(self.suppliers_note.id))
        expected_message = ORDERS_ERROR_RESPONSES[
            "supplier_note_deletion_validation_error"]
        self.assertEqual(
            expected_message, response['errors'][0]['message'])

    def test_delete_suppliers_note(self):
        """Test method for deleting suppliers note"""
        response = self.query_with_token(
            self.access_token_master,
            delete_supplier_note(self.supplier_note_factory.id))
        self.assertIn(SUCCESS_RESPONSES[
                      "deletion_success"].format("Supplier's note"),
                      response["data"]["deleteSuppliernote"]["success"])
        self.assertNotIn("errors", response)
