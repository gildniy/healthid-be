from healthid.apps.orders.enums.suppliers import PaymentTermsType


def check_payment_terms(payment_terms):
    is_payment_term_valid = False
    for choice in PaymentTermsType.choices():
        is_payment_term_valid = payment_terms in choice
        if is_payment_term_valid:
            break
    return is_payment_term_valid
