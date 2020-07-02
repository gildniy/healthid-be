
create_stock_template_string = '''
        mutation{{
        createStockCountTemplate(
            productIds:{product_ids}
            assignedUserIds:{assigned_user_ids}
            designatedUserIds:{dessignate_user_ids}
            outletId:{outlet_id}
            eventTypeId:{event_type_id}
            interval:{interval}
            startDate:{start_date}
            endDate:{end_date}
            endOn: {end_on}
        ){{
            stockTemplate{{
            id
            products{{
                pageInfo{{
                hasNextPage
                hasPreviousPage
                endCursor
                }}
                edges{{
                node{{
                    productName
                    id
                    unitCost
                }}
                }}
            }}
            assignedUsers{{
                    id
            }}
            designatedUsers{{
                id
                role{{
                name
                }}
            }}
            }}
            success
        }}
        }}
'''


edit_stock_template_string = '''
        mutation{{
        editStockCountTemplate(
            templateId:{template_id}
            productIds:{product_ids}
            assignedUserIds:{assigned_user_ids}
            designatedUserIds:{dessignate_user_ids}
            outletId:{outlet_id}
            eventTypeId:{event_type_id}
        ){{
            stockTemplate{{
            id
            products{{
                pageInfo{{
                hasNextPage
                hasPreviousPage
                endCursor
                }}
                edges{{
                node{{
                    productName
                    id
                    unitCost
                }}
                }}
            }}
            assignedUsers{{
                    id
            }}
            designatedUsers{{
                id
                role{{
                name
                }}
            }}
            }}
            success
        }}
        }}
'''

delete_stock_template_string = '''
        mutation deleteTemplate{{
        deleteStockCountTemplate(templateId:{id}){{
            success
            errors
        }}
        }}
'''


query_all_templates = '''
        query {{
        stockTemplates(outletId:{outlet_id}) {{
            id
            assignedUsers {{
            id
            email
            }}
            designatedUsers {{
            id
            email
            }}
            createdAt
            outlet {{
            id
            name
            }}
            scheduleTime {{
            eventTitle
            description
            }}
            products{{
            edges{{
                node{{
                id
                productName
                }}
            }}
            }}
        }}
        }}

'''

query_single_template = '''
        query singleTemplate {{
        stockTemplate(templateId:{template_id}, outletId:{outlet_id}) {{
            id
            assignedUsers {{
            id
            email
            }}
            designatedUsers {{
            id
            email
            }}
            scheduleTime {{
            eventTitle
            description
            }}
            products {{
            edges {{
                node {{
                id
                productName
                }}
            }}
            }}
        }}
        }}

'''

initate_stock_count_query = '''
mutation initiateStock{{
  initiateStock(
    isCompleted:false,
    batchInfo: ["{batchInfo}"],
    product: {product},
    quantityCounted:[{quantityCounted}],
    remarks: "Don't ever tell me to count this stock again",
    stockTemplateId: {stockTemplateId},
    varianceReason: {varianceReason}
    specifyReason: "Was returned"
  ) {{
    errors
    message
    stockCount {{
      id
      varianceReason
      product {{
        id
        productName
      }}
      stockTemplate {{
        id
      }}
    }}
  }}
}}

'''

no_variance_reason_query = '''
mutation initiateStock{{
  initiateStock(
    isCompleted:false,
    batchInfo: ["{batchInfo}"],
    product: {product},
    quantityCounted:[{quantityCounted}],
    remarks: "Don't ever tell me to count this stock again",
    stockTemplateId: {stockTemplateId},
    varianceReason: {varianceReason}
    specifyReason: ""
  ) {{
    errors
    message
    stockCount {{
      id
      varianceReason
      createdAt
      updatedAt
      isCompleted
      isApproved
      product {{
        productName
        id
      }}
      stockTemplate {{
        id
        assignedUsers {{
          id
          email
        }}
      }}
    }}
  }}
}}
'''

update_stock_count_query = '''
  mutation {{
  updateStock (
    stockCountId:"{stockCountId}",
    batchInfo: ["{batchInfo}"],
    isCompleted: {isCompleted},
    product: {product},
    quantityCounted: [{quantityCounted}]
    varianceReason: Others
    specifyReason: "it expired"
  ){{
    message
    errors
    stockCount{{
      id
      varianceReason
      product {{
        id
        productName
      }}
       stockTemplate {{
        id
        assignedUsers {{
          id
          email
        }}
      }}
    }}
  }}
}}
'''

all_stock_counts = '''
query {
  stockCounts {
    id
    isApproved
    isCompleted
    varianceReason
  }
}
'''

single_stock_count = '''
query {{
  stockCount(id:"{stockCountId}") {{
    id
    isCompleted
    varianceReason
    product {{
      id
    }}
  }}
}}
'''

delete_stock_batch = '''
mutation {{
  removeBatchStock (
    batchInfo: "{batchInfo}",
    stockCountId: "{stockCountId}",
  ) {{
    message
    errors
    stockCount {{
      id
    }}
  }}
}}
'''

all_approved_stock_count = '''
query{
  approvedStockCounts{
    id
    varianceReason
    isApproved
    remarks
    createdAt
    product{
      id
      productName
      }
    stockTemplate{ id
     }
  }
}
'''

all_unresolved_stock_count = '''
query{
  unresolvedStockCounts{
    id
    varianceReason
    isApproved
    remarks
    createdAt
    product{
      id
      productName
      }
    stockTemplate{id products{edges{node{
      id
       productName
       }
       }
       }
       }
  }
}
'''
approve_stock_count = '''
mutation reconcileStock{{
    reconcileStock(
        batchInfo: ["{batchInfo}"],
        stockCountId: "{stockCountId}",
    ){{
        message
        stockCount{{
            isApproved
            varianceReason
            stockTemplate{{
                      isClosed
                    }}
            product{{
                quantityInStock
                id
                batchInfo{{
                    id
                    quantity
                    comment
                    dateReceived
                    batchNo
                }}
            }}
        }}

    }}
}}
'''

approve_stock_count_without_batch_ids = '''
mutation reconcileStock{{
    reconcileStock(
        batchInfo: [],
        stockCountId: "{stockCountId}"
    ){{
        message
    }}
}}
'''

open_stock_transfer = """
  mutation{{
    openStockTransfer(
      batchIds: ["{batch_ids}"],
      destinationOutletId: {outlet_id},
      productId: {product_id},
      quantities: [{quantity}]
  ){{
      stockTransfer{{
      id,
      sendingOutlet{{
          name
      }},
      destinationOutlet{{
          name
      }},
      createdAt,
      completeStatus
      }}
      success
  }}
}}
"""

view_stock_transfers = """
            query{
        stockTransfers{
            id,
            sendingOutlet{
            name,
            id
            },
            destinationOutlet{
            name,
            id
            },
            createdAt,
            completeStatus
        }
        }
"""

close_stock_transfer = """
        mutation{{
        closeStockTransfer(
            transferNumber: "{transfer_number}"
        ){{
            success
        }}
        }}
"""

view_stock_transfer = """
            query{{
            stockTransfer(transferNumber: "{transfer_number}"){{
                id,
                sendingOutlet{{
                name,
                id
                }},
                destinationOutlet{{
                name,
                id
                }},
                createdAt,
                completeStatus
            }}
            }}
"""
