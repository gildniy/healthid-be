SALES_SUCCESS_RESPONSES = {
    "promotion_approval_success": "Promotion has been approved",
    "sales_prompt_create_success": "Successfully created {sales_prompt_count} "
                                   "sales prompt",
    "add_to_cart_success": "Product added to cart.",
    "sale_intiate_success": "Return was initiated successfully",
    "calculated_velocity":  "Sales velocity calculated successfully."
                            "Use calculated value",
    "sales_return_approved": "Sales return approved successfully",
    "create_sales_success": "Sale was created successfully"
}

SALES_ERROR_RESPONSES = {
    "outlet_validation_error": "You don\'t belong to outlet "
                               "with this promotion.",
    "promotion_type_error": "Please provide promotion type name.",
    "incomplete_list": "List inputs are incomplete or empty",
    "title_error": "Titles and description must contain words",
    "unapproved_product_error": "{} isn't approved yet.",
    "in_stock_product_error": "There is only quantity "
                              "{} of {} available in stock.",
    "inexistent_promotion": "Promotion with id {} does not exist.",
    "outlet_id_validation_error": "You don't belong to outlet with id {}.",
    "default_velocity": "Not enough sales data to calculate sales velocity."
                        "Please use default value",
    "less_quantities": "Batches with ids '{}' do not have enough" +
    " quantities to be sold",
    "negative_integer": "Price for batches with ids '{}' should" +
    "be positive integer",
    "negative_discount": "Batches with ids '{}' can't have negative discount",
    "not_returnable": "Products with ids {} are not returnable",
    "already_approved_sales_returns":
        "Sales returns with ids {} already approved",
    "empty_sales_return": "Sales return can't be empty!",
    "no_sales_error": "No sales to view yet!",
    "less_credit": "You do not have enough credit to purchase these items",
    "invalid_payment": "The payment method is not valid in this outlet",
    "invalid_amount": "Amount should be greater than 1",
    "invalid_discount": "Discount must be greater between 0 and 100",
    "wrong_currency": "Customer wallet currency must be the same as"
    " the outlet currency",
    "already_marked_as_paid": "This consultation is already marked as paid",
    "provide_date_from": "Please provide a dateFrom with dateTo arguments!",
    "payment_descrepancy": "The amount to be paid and the amount paid via different methods are not equal",
    "sales_does_not_exist": "Sales does not exist"
}

SALE_METHODS_MAP = {
    "CASH": "Cash",
    "CARD": "Card",
    "BANK_TRANSFER": "Bank_Transfer"
}
