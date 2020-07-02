
create_sales_prompts = '''
mutation{{
  createSalesprompts(
    productIds:[{product_id}],
    outletIds:[{outlet_id}],
    promptTitles:["{title}"],
    descriptions:["{description}"]
  ){{
  message
  }}
  }}

'''

incomplete_sales_entry = '''
mutation{{
  createSalesprompts(
    productIds:[{product_id},{product_id}],
    outletIds:[{outlet_id}],
    promptTitles:["{title}"],
    descriptions:["{description}"]
  ){{
  message
  }}
  }}

'''

update_sales_prompt = '''
mutation{{
   updateSalesprompt(id:{sales_prompt_id},
    promptTitle:"{title}",
    description:"{description}",
    productId:{product_id},
    outletId:{outlet_id}){{
    salesPrompt{{
      id
      promptTitle
      description
    }}
    success
  }}
}}

'''

create_sales_performance_query = '''
mutation {{
  createSalesPerformance(
    saleId:{sale_id},
    productId:{product_id},
    cashierId:"{cashier_id}",
    customerId:{customer_id},
    outletId:{outlet_id},
    discount:{discount},
    unitPrice:{unit_price},
    quantitySold:{quantity_sold},
    subtotal:{subtotal},
    transactionDate:"2020-01-10"
  ){{
    salePerformance{{
      id,
      subtotal
    }}
  }}
}}
'''

get_sales_performance_outlet_filter = '''
{{
  salePerformances(
    outlets:{outlets_list}
  ) {{
    edges {{
      node {{
        id,
        transactionDate,
        outlet{{
          id
        }}
      }}
    }}
  }}
}}
'''

get_sales_performance = '''
{
  salePerformances{
    edges {
      node {
        id,
        transactionDate,
        outlet{
          id
        }
      }
    }
  }
}
'''


def delete_sales_prompt(sales_prompt_id):
    return f'''mutation{{
                deleteSalesprompt(id: {sales_prompt_id}){{success}}
                    }}'''


query_all_sales_prompt = '''
        query{
         salesPrompts{
                id
                promptTitle
                description
                product{
                  id
                  productName
                }
               }
}
'''


def query_a_sales_prompt(sales_prompt_id):
    return (f'''query{{salesPrompt(id: {sales_prompt_id}){{id}}}}''')


def create_promotion(promotion):
    return (f'''
            mutation {{
                createPromotion(
                    title: "{promotion['title']}",
                    promotionTypeId: "{promotion['promotion_type_id']}",
                    description: "{promotion['description']}",
                    discount: {promotion['discount']},
                    outletId: {promotion['outlet_id']}
                    ) {{
                    success
                    promotion {{
                        id
                    }}
                }}
            }}
    ''')


def retrieve_promotions(outlet_id):
    return (f'''
            query {{
                outletPromotions(outletId: {outlet_id}){{
                    id
                }}
            }}
    ''')


def update_promotion(promotion_id, promotion):
    return (f'''
            mutation {{
                updatePromotion(
                    promotionId: "{promotion_id}"
                    title: "{promotion}"
                ){{
                    success
                    promotion {{
                        id
                    }}
                }}
            }}
    ''')


def delete_promotion(promotion_id):
    return (f'''
            mutation {{
                deletePromotion(
                    promotionId: "{promotion_id}"
                ){{
                    success
                }}
            }}
    ''')


def create_promotion_type(name):
    return (f'''
            mutation {{
                createPromotionType(
                    name: "{name}"
                    ) {{
                    success
                    promotionType {{
                        id
                    }}
                }}
            }}
    ''')


def retrieve_promotion_types():
    return (f'''
            query {{
                promotionTypes{{
                    id
                }}
            }}
    ''')


def approve_promotion(promotion_id):
    return (f'''
            mutation {{
                approvePromotion(promotionId: "{promotion_id}"){{
                    success
                    promotion {{
                        id
                    }}
                }}
            }}
    ''')


def retrieve_promotions_pending_approval(outlet_id):
    return (f'''
            query {{
                promotionsPendingApproval(outletId: {outlet_id}){{
                    id
                }}
            }}
    ''')


def add_to_cart(product_id, quantity):
    return (f'''
            mutation {{
                addToCart(productId: {product_id}, quantity: {quantity}) {{
                    success
                    cartItem {{
                        id
                    }}
                }}
            }}
    ''')


def retrieve_cart():
    return (f'''
            query {{
                cart {{
                    id
                    items {{
                        product {{
                            id
                        }}
                        quantity
                    }}
                }}
            }}
    ''')


create_sale = '''
mutation {{
  createSale(
      discountTotal: {discount_total},
      amountToPay: {amount_to_pay},
      paymentMethod:"{payment_method}",
      customerId:"{customer_id}"
      outletId: {outlet_id}
      subTotal: {sub_total},
      changeDue: {change_due},
      paidAmount: {paid_amount},
      batches: [
          {{
              batchId: "{batchId}",
              quantity: {quantity},
              discount: {discount},
              price: {price}
          }}
        ]
      )
      {{
    sale {{
      id
      createdAt
    }}
    receipt {{
      id
    }}
    message
  }}
}}
'''

create_sale_with_empty_batches = '''
mutation {{
  createSale(
      discountTotal: {discount_total},
      amountToPay: {amount_to_pay},
      paymentMethod:"{payment_method}",
      customerId:"{customer_id}"
      outletId: {outlet_id}
      subTotal: {sub_total},
      changeDue: {change_due},
      paidAmount: {paid_amount},
      batches: []
      )
      {{
    sale {{
      id
      createdAt
    }}
    receipt {{
      id
    }}
    message
  }}
}}
'''


create_anonymous_sale = '''
mutation {{
  createSale(
      discountTotal: {discount_total},
      amountToPay: {amount_to_pay},
      paymentMethod:"{payment_method}",
      outletId: {outlet_id}
      subTotal: {sub_total},
      changeDue: {change_due},
      paidAmount: {paid_amount},
      batches: [
          {{
              batchId: "{batchId}",
              quantity: {quantity},
              discount: {discount},
              price: {price}
          }}
        ]
      )
      {{
    sale {{
      id
    }}
    receipt {{
      id
    }}
    message
  }}
}}'''


def query_sales_history(outlet_id):
    return (f'''
            query {{
                outletSalesHistory(outletId: {outlet_id}){{
                    id
                    createdAt
                    discountTotal
                }}
            }}
    ''')


def query_sales_history_date_fail(outlet_id):
    return (f'''
            query {{
                outletSalesHistory(
                    outletId: {outlet_id}
                    dateFrom: "2018-03-13T09:55:24+00:00"
                    dateTo: "2018-03-13T11:55:24+00:00"){{
                    id
                    discountTotal
                }}
            }}
    ''')


def query_sales_history_date_fail_two(outlet_id):
    return (f'''
            query {{
                outletSalesHistory(
                    outletId: {outlet_id}
                    dateTo: "2018-03-13T11:55:24+00:00"){{
                    id
                    discountTotal
                }}
            }}
    ''')


def query_sales_history_date_ok(outlet_id, date_from, date_to):
    return (f'''
            query {{
                outletSalesHistory(
                    outletId: {outlet_id}
                    dateFrom: "{date_from}"
                    dateTo: "{date_to}"){{
                    id
                    discountTotal
                }}
            }}
    ''')


def query_sale_history(sale_id):
    return (f'''
            query {{
                saleHistory(saleId: {sale_id}){{
                    id
                    changeDue
                }}
            }}
    ''')


sales_velocity_query = '''
    query{{
      salesVelocity(
        productId: {product_id},
        outletId: {outlet_id}
        ){{
        defaultSalesVelocity
        calculatedSalesVelocity
        message
        }}
    }}
'''


all_sales_history_query = '''
    query{
         allSalesHistory{
                id
        }
    }
'''

generate_custom_near_expire_promos = '''
    mutation{{
      createCustomNearExpirePromotion(productId:{product_id},
      promotionId:"{promotion_id}",
      applyMonths:{apply_months}){{
        success
      }}
    }}
'''


query_team_report = '''
           query{
                teamReport(
                    dateFrom: "2019-03-23T00:00:24+00:00",
                    dateTo: "2021-03-23T16:29:17+00:00",
                    pageNumber: 1,
                    pageCount: 1
                ){
                    sale{
                    salesPerson{
                        email
                        role{
                        name
                        }
                    }
                    }
                    totalQtySold
                    totalProductsSold
                    totalCashAmount
                    totalCardAmount
                }
                }
    '''
