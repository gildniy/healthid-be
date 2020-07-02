create_customer_credit = '''
    mutation{{
        createCustomerCredit(
            customerId:{customer_id},
        )
        {{
            message
            customerCredit{{
            storeCredit
            creditCurrency{{
                id
                name
            }}
            customer{{
                id
                firstName
                lastName
                email
            }}
            }}
        }}
    }}
'''

edit_credit = '''
    mutation {{
        editCustomerWallet(
            customerId:{customer_id},
            storeCredit:{store_credit}
        ){{
    message
    customer{{
      storeCredit
   }}
  }}
}}
'''

store_credit_query_all = '''
query {
    customerCredits {
        storeCredit
    }
}
'''

customer_id_store_credit_query = '''
query {{
    customerCredit(customerId: {customer_id}) {{
        storeCredit
    }}
}}
'''

customer_credit_pagination_query = '''
query {{
    customerCredits(pageCount: {}, pageNumber: {}) {{
        storeCredit
    }}
}}
'''

customer_credit_invalid_argument = '''
query {{
    customerCredit{}({}) {{
        storeCredit
    }}
}}
'''
