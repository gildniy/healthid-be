batch_expiry_query = '''
query{
  batchExpiries(endDate:"2019-05-30"){
      id
      batchNo
      expiryDate
        supplier{
            name
            }
        }
    }
'''
wrong_expiry_date = '''
query{
  batchExpiries(
    date:"2019-30"
    ){
        id
        batchNo
        expiryDate
    supplier{
      name
    }
    }
}
'''

query_expired_products = '''
query{
  expiredBatches{
    id
    batchNo
    expiryDate
    supplier{
      name
    }
  }
}
'''

generate_recommended_promos = '''
mutation{{
  createRecommendedPromotion(outletId:{outlet_id}){{
    success
  }}
}}
'''
