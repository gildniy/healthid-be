ORDERS_SUCCESS_RESPONSES = {
    "scan_save_success": "Scan successfully saved",
    "add_order_note_success": "A supplier order note successfully added",
    "invoice_upload_success": "Invoice uploaded successfully",
    "order_initiation_success": "Order successfully initiated!",
    "order_addition_success": "Successfully added order details!",
    "supplier_approval_success": "supplier {} has been approved!",
    "supplier_deletion_success": "supplier {} has been deleted!",
    "supplier_edit_request_success": "Edit request for Supplier {} "
                                     "has been sent!",
    "supplier_edit_request_update_success": "Edit request for Supplier {} "
                                            "has been updated!",
    "supplier_update_success": "Supplier {} has been successfully updated!",
    "supplier_order_email_success": "Supplier Order Forms "
                                    " {} successfully sent.",
    "supplier_order_approval_success": "Supplier Order Details"
                                       " of id {} successfully approved.",
    "supplier_order_marked_closed": "Supplier Order Details"
                                    " of id {} placed and auto-sent successfully to the supplier.",
    "already_closed_order": "Order {} already closed",
    "order_close_success": "Order {} closed successfully",
    "supplier_order_mark_status": "Supplier Order Details"
                                       " of id {} status marked approved.",
}

ORDERS_ERROR_RESPONSES = {
    "duplicate_upload_error": "An invoice for this order already exists",
    "initiation_invoice_upload_error": "Cannot upload Invoice. Your outlet "
                                       "did not initiate this order",
    "supplier_edit_proposal_validation_error": "You can only propose an edit "
                                               "to an approved supplier!",
    "supplier_edit_validation_error": "You can only edit an "
                                      "approved supplier!",
    "edit_proposal_validation_error": "You can't edit an edit request "
                                      "you did not propose!",
    "supplier_note_length_error": "Suppliers note must be two or more words",
    "supplier_note_update_validation_error": "You can't update a note you "
                                             "didn't create",
    "supplier_note_deletion_validation_error": "You can't delete a note "
                                               "you didn't create",
    "supplier_search_key_error": "Please provide a valid search keyword",
    "inexistent_supplier_search_error": "Supplier matching query"
                                        "does not exist!",
    "supplier_request_denied": "Edit request for supplier {} "
                               "has been declined!",
    "scan_order_rejection": "Scan rejected: this order"
                            " is not marked closed.",
    "scan_batch_rejection": "Scan rejected: BatchInfo does"
                            " not match the provided outlet",
    "scan_product_rejection": "Scan rejected: Product does"
                              " not match the provided BatchInfo",
    "scan_disabled": "Barcode scanning is disabled",
    "close_order_invalid_user": "Cannot close order in outlet you're "
                                "not active in",
    "invalid_supplier_field": "Please provide the right field of "
                                "supplier name or id",
    "invalid_email": "Please input a valid email",
    "invalid_mobile": "Please input a valid phone",
    "invalid_supplier_email": "Please input a valid email",
    "invalid_supplier_phone": "Please input a valid phone",
    "invalid_rating": "The {} should be between 0 and {}",
    "supplier_order_not_approved":
    "Can't set status to approved, supplier order form not approved yet",
    "no_supplier_order_id": "supplier order details of id {} doesnot exist",
    "none_supplier_order_id": "supplier order details id not provided",
    "not_allowed_to_edit_this_supplier": "You are not allowed to edit this supplier",
    "supplier_revision_not_found": "Supplier Revision of id {} not found!",
    "supplier_revision_not_allowed": "You cannot approve this supplier's revision",
    "inexistent_batch": "Batch with Parameters {}:{} do not exist"
}
