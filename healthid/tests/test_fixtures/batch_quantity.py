propose_quantity = '''
mutation proposeQuantity {{
   proposedQuantity (
    batchIds: ["{batch_id}"]
    productId: {product_id},
    proposedQuantities: [11],

  ) {{
    notification
    batchInfo {{
      batchNo
      expiryDate
      dateReceived
      quantity
      supplier{{
        name
      }}
      unitCost,
      quantity,
      comment,
      unitCost
    }}
  }}
}}
'''

propose_quantity2 = '''
mutation proposeQuantity {{
   proposedQuantity (
    batchIds: ["{batch_id}"]
    productId: {product_id},
    proposedQuantities: [11, 90],

  ) {{
    notification
    batchInfo {{
      batchNo
      expiryDate
      dateReceived
      quantity
      supplier{{
        name
      }}
      unitCost,
      quantity,
      comment,
      unitCost
    }}
  }}
}}
'''

approve_quantity = '''
mutation approveProposedQuantity {{
   approveQuantity (
    batchIds: ["{batch_id}"],
    productId: {product_id},
    isApproved: {value},
    comment: "Reject"


  ){{
   message
   quantityInstance{{
    id
    isApproved
    quantityReceived
    authorizedBy{{
      id
      email
    }}
  }}
  }}
}}
'''
