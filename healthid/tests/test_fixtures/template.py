def create_template(outlet_id):
    return (f'''
                mutation{{
                createReceiptTemplate(
                    cashier: false,
                    discountTotal: false,
                    outletId: {outlet_id},
                    totalTax: false,
                    subtotal: true,
                    purchaseTotal: false,
                    changeDue: true,
                    loyalty: false,
                    loyaltyEarned: true,
                    loyaltyBalance: false,
                    barcode: true,
                    amountToPay: false,
                    receipt: false,
                    receiptNo: false,
                )
                {{
                    receiptTemplate{{
                    cashier
                    }}
                }}
                }}
            ''')


def update_template(template_id):
    return (f'''
            mutation{{
                updateReceiptTemplate(
                    id: \"{template_id}\",
                    cashier: true,
                    discountTotal: true,
                    totalTax: false,
                    subtotal: true,
                    purchaseTotal: false,
                    changeDue: true,
                    loyalty: false,
                    loyaltyEarned: true,
                    loyaltyBalance: false,
                    amountToPay: false,
                    receipt: false,
                    receiptNo: false,
                )
                {{
                    receiptTemplate{{
                    id
                    cashier
                    discountTotal
                    }}
                }}
            }}
            ''')


def delete_template(template_id):
    return f'''mutation{{
                deleteReceiptTemplate(id: \"{template_id}\"){{success}}
                    }}'''


def query_template(template_id):
    return (f'''query{{receiptTemplate(id: \"{template_id}\"){{id}}}}''')
