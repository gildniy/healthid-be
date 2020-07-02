mail_receipt = '''
mutation{{
  mailReceipt(receiptId:"{receipt_id}") {{
    message
  }}
}}
'''
