initiate_sales_return_query = '''
mutation{{
  initiateSalesReturn(outletId:{outlet_id}
    saleId: {sale_id}
    returnAmount:6000
    returnNote: "bad product"
    refundCompensationType: Cash
  returnedBatches:[{{batchId: "{batch_id}",
    quantity: 1, price: 3000,
    resellable: false,
    returnReason: ExpiredProduct}}]
  ){{
    message
    salesReturnInitiated{{
      id
      salereturndetailSet{{
        id
      }}
    }}
  }}
}}
'''


approve_sales_return = '''
mutation{{
  approveSalesReturn(
    salesReturnId: {sales_return_id},
    salesId: {sale_id},
    returnedSales: {returned_sales_ids}
    ){{
      message
    }}
  }}
'''
