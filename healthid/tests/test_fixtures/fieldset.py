def create_fieldset(template_id, sale_id):
    return (f'''
                mutation{{
                    createFieldSet(
                        receiptTemplateId: \"{template_id}\",
                        saleId: {sale_id}
                )
                {{
                    fieldSet{{
                    id
                    }}
                }}
                }}
            ''')


def update_fieldset(fieldset_id):
    return (f'''
            mutation{{
                updateFieldSet(
                    id: \"{fieldset_id}\",
                    cashier: "No cashier",
                    discountTotal: "Discounted by",
                    totalTax: "A tax of",
                    subtotal: "subtotal of",
                    purchaseTotal: "total",
                    changeDue: "your change",
                    loyalty: "loyalty yes",
                    loyaltyEarned: "new points",
                    loyaltyBalance: "total points",
                    amountToPay: "pay",
                    receipt: "your receipt",
                    receiptNo: "no",
                    footer: "Thank you for coming here",
                )
                {{
                    fieldSet{{
                    id
                    cashier
                    }}
                }}
            }}
            ''')


def delete_fieldset(fieldset_id):
    return f'''mutation{{
                deleteFieldSet(id: \"{fieldset_id}\"){{success}}
                    }}'''


retrieve_receipts = '''
query {
  receipts {
    id
  }
}
'''

retrieve_receipt = '''
query {{
  receipt(receiptId: "{receipt_id}") {{
    id
  }}
}}
'''
