barcode_scan = '''
mutation{{
  recordScan(
    batchId: "{batch_id}",
    orderId: {order_id},
    scannedNumber: "{scanned_number}",
    outletId: {outlet_id},
    productId: {product_id},
    count: {count}
    ){{
    barcodeScan {{
      id
      scannedNumber
    }}
  }}
}}
'''
