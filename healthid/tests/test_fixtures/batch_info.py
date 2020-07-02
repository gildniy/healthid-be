batch_info_query = '''
mutation createBatchInfo {{
createBatchInfo (
    supplierId: "{supplier_id}",
    productId: {product_id},
    dateReceived: "2019-12-03",
    quantity: 10,
    expiryDate: "{expiry_date}",
    unitCost: 100,
    comment: "5 packs pending",
    deliveryPromptness: true,
    serviceQuality: 3
  ) {{
    message
    batchInfo {{
      id
      batchNo
      expiryDate
      dateReceived
      supplier{{
        name
      }}
      unitCost
      outlet{{
        id
      }}
    }}
  }}
}}
'''

update_batch_info = '''
mutation updateBatchInfo {{
updateBatchInfo (
    batchId: "{batch_id}",
    supplierId: "{supplier_id}",
    dateReceived: "2019-04-12",
    expiryDate: "2020-04-02",
    unitCost: 50,
    deliveryPromptness: true,
    quantityRemaining: 33,
    serviceQuality: 5
  ) {{
    message
    batchInfo {{
      batchNo
      expiryDate
      dateReceived
      supplier{{
        name
      }}
      batchQuantities {{
        quantityReceived
        quantityRemaining
      }}
      unitCost,
      comment
      unitCost
    }}
  }}
}}
'''

query_product_batch_info = '''
query {{
  productBatchInfo (id:{product_id}){{
    batchNo
    quantity
    unitCost
    supplier {{
      id
      name
    }}
  }}
}}
'''

single_batch_info = '''
query {{
  batchInfo (id:"{batch_id}") {{
    batchNo
    supplier {{
      id
      name
    }}
    unitCost
    dateReceived
  }}
}}
'''

all_batch_info = '''
query {
 allBatchInfo {
   product {
      id
   }
   batchNo
      supplier {
        name
      }
      unitCost
      quantity
      }
      }
'''

delete_batch_info = '''
mutation deleteBatchInfo {{
  deleteBatchInfo (batchId:"{batch_id}") {{
    message
  }}
}}
'''

near_expired_batches = '''
query {
 nearExpiredBatches {
    id
    expiryDate
}
}
'''
