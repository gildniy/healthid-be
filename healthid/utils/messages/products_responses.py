PRODUCTS_SUCCESS_RESPONSES = {
    "survey_deletion_success": "Survey id, {}, and all its associated price "
                               "checks have been deleted!",
    "edit_request_success": "Edit request for quantity has been sent!",
    "set_price_success": "The {key} of {number} product(s) has"
    " successfully been updated to {value}",
    "approval_pending": "Proposed update pending approval",
    "edit_request_decline": "Edit request for product {} has been declined!",
    "product_activation_success": "Products with ids {} have been activated.",
    "product_deactivation_success": "Products with ids {} have been "
                                    "deactivated.",
    "batch_edit_proposal": "Batch no: {} has a"
                           " proposed quantity edit.",
    "low_quantity_alert": "Low quantity alert! "
                          "Product name: {}, Unit(s) left: {}.",
    "proposal_approval_success": "Proposal for change in quantity of {}"
                                 " received on {} has been approved",
    "batch_upload_success": "Successfully uploaded batch CSV information.",
    "loyalty_weight_updated": "The Loyalty weight of {} products has successfully been updated to {}"
}

PRODUCTS_ERROR_RESPONSES = {
    "request_approval_error": "Batches with ids {} have pending requests.",
    "unapproved_product_batch_error": "{} is not approved thus cannot "
                                      "create a batch.",
    "wrong_proposed_edit_id": "Product {} has no proposed edit with id {}",
    "inexistent_proposal_error": "Proposal for this product "
                                 "doesn't exist",
    "invalid_input_error": "This name field can't be empty",
    "survey_update_error": "This survey has already been closed. "
                           "It cannot be updated!",
    "batch_match_error": "The number of batches and quantities "
                         "provided do not match",
    "inexistent_batches": "Batches with ids {} do not exist in this product",
    "product_prompt": "Please specify at least one product.",
    "supplier_prompt": "Please specify at least one supplier.",
    "approve_deletion_error": "Approved product can't be deleted.",
    "loyalty_weight_error": "Loyalty weight can't be set below one",
    "invalid_search_key": "Please provide a valid search keyword",
    "inexistent_product_query": "Product matching search query does not exist",
    "product_approval_duplication": "Product {} has already been approved",
    "inexistent_proposed_edit": "No proposed edit with id {}",
    "product_activation_error": "Product with id {} does not exist or "
                                "is already activated.",
    "product_deactivation_error": "Product with id {} does not exist or "
                                  "is already deactivated.",
    "proposal_decline": "Proposal for change in quantity of {} received on {} "
                        "has been declined",
    "inexistent_supplier": "Suppliers with id {} does not exist.",
    "inexistent_product": "Product with id {} does not exist.",
    "inexistent_batchinfo": "BatchInfo with id {} does not exist.",
    "closed_survey_error": "This survey has already been closed",
    "product_category_no_edits": "Product category unchanged, "
                                 "nothing to edit.",
    "default_product_category_error": "You cannot delete a default "
                                      "product category",
    "invalid_batch_quality": "Service quality must be an integer "
                             "between 1 and 5",
    "wrong_param": "Please provide a valid param in the url",
    "batch_csv_error": "CSV file improperly formatted. The batch "
                       "information columns must be ordered as follows:"
                       "Product,Supplier,Date Received,"
                       "Expiry Date,Unit Cost,Quantity Received,"
                       "Service Quality,Delivery Promptness",
    "batch_bool_error": "Please ensure eiether 'True' or 'False' is "
                        "entered in the 'Delivery Promptness' column.",
    "batch_expiry_error": "The batch for product '{}' has expired. "
                          "Please check its expiry and delivery dates.",
    "promotion_generated_success": "{}, generated successfully!",
    "update_price_error": "You can update only one value, either "
                            "markup or sales_price"
}
