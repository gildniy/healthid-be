from healthid.apps.products.models import Product

create_product = '''
        mutation{{
            createProduct(
                productCategoryId:1,
                productName :"panadol",
                dispensingSizeId :1,
                description :"first treatment people try for mild to moderate pain",  # noqa E501
                brand :"ventolinllke",
                manufacturer:"Harmon Northrop",
                vatStatus:true,
                loyaltyWeight: 1
                preferredSupplierId :"{supplier_id}",
                backupSupplierId:"{backup_id}",
                tags :["painkillers"],
                globalUpc: "{global_upc}",
                reorderPoint: 5,
                reorderMax: 10
                    ){{
                product{{
                    id
                    tags
                    salesPrice
                    productName
                    vatStatus
                    globalUpc
                    reorderPoint
                    reorderMax
                }}
            }}
            }}
'''

supplier_mutation = '''
        mutation{
          addSupplier(
            input:{
              name: "supplier.",
              tierId: 1
            },
            contactsInput: {
              email: "email@supplier.com",
              mobileNumber:"+256702260027",
              addressLine1:"address",
              addressLine2:"addressline2",
              lga: "lga",
              cityId: 1
              countryId:1,
            },
            metaInput: {
              displayName: "this is a display name"
              creditDays:4,
              logo:"logo",
              paymentTerms: "ON_CREDIT",
              commentary: "no comment"
            }
          ){
            supplier{
              id
              name
              tier { name }
              supplierContacts{
                email
                mobileNumber
                addressLine1
                city {
                  name
                  }
                country{
                  name
                }
              }
              supplierMeta{
                displayName
                creditDays
                logo
                paymentTerms
                commentary
              }
            }
          }
        }
'''
create_proposed_product = '''
mutation {{
    createProduct(
        productCategoryId:1,
        productName :"gfcds",
        dispensingSizeId :1,
        description :"first treatment people try for mild to moderate pain",
        brand :"ventolinllke mklllll",
        manufacturer:"vbn",
        vatStatus: true,
        loyaltyWeight: 1
        preferredSupplierId : "{0}",
        backupSupplierId:"{0}",
        tags:["painkillers","panadol"]

    ){{
      product{{
        id
        salesPrice
        productName
        vatStatus
        skuNumber
        tags
      }}

    }}
}}
'''
backup_supplier = '''
        mutation{
          addSupplier(
            input:{
              name: "backup supplier",
              tierId: 1
            },
            contactsInput: {
              email: "email@backupsupplier.com",
              mobileNumber:"+256702260027",
              addressLine1:"address",
              addressLine2:"addressline2",
              lga: "lga",
              cityId: 1
              countryId:1,
            },
            metaInput: {
              creditDays:4,
              logo:"logo",
              paymentTerms: "ON_CREDIT",
              commentary: "no comment"
            }
          ){
            supplier{
              id
              name
              tier { name }
              supplierContacts{
                email
                mobileNumber
                addressLine1
                city {
                  name
                }
                country {
                  name
                }
              }
              supplierMeta{
                displayName
                creditDays
                logo
                paymentTerms
                commentary
              }
            }
          }
        }
'''

approved_product_query = '''
query{
    approvedProducts {
        skuNumber
        productName
    }
}
'''

proposed_product_query = '''
query{
    proposedProducts {
        skuNumber
        productName
        globalUpc
    }
}
'''


def create_product_2(supplier_id, backup_id, user, business):
    return Product.objects.create(
        product_category_id=1,
        product_name='Panadol',
        dispensing_size_id=1,
        description='first treatment people try',
        brand='ventolinllke',
        manufacturer="Harmon Northrop",
        vat_status=True,
        sales_price=1000,
        preferred_supplier_id=supplier_id,
        backup_supplier_id=backup_id,
        tags="painkillers",
        is_approved=True,
        business=business,
        user=user)


def create_new_product(name, description, brand, manufacturer,
                       category, supplier_id, backup_id, user, business, is_approved=True, global_upc=None):
    return Product.objects.create(
        product_category=category,
        product_name=name,
        dispensing_size_id=1,
        description=description,
        brand=brand,
        manufacturer=manufacturer,
        vat_status=True,
        sales_price=1000,
        preferred_supplier_id=supplier_id,
        backup_supplier_id=backup_id,
        tags="painkillers",
        is_approved=is_approved,
        business=business,
        user=user)


def update_product(product_id, product_name, global_upc=None, reorder_point=None, reorder_max=None):
    return (f'''
            mutation {{
                updateProduct(
                    id: {product_id},
                    productName: "{product_name}",
                    description :"forever younger",
                    brand :"ventolinllke",
                    manufacturer:"Harmon",
                    vatStatus:true,
                    salesPrice :1400,
                    tags :["painkillers","headache"],
                    globalUpc: "{global_upc}",
                    reorderPoint: {reorder_point},
                    reorderMax: {reorder_max},
                ){{
                product{{
                    productName
                    id
                    user{{id}}
                    globalUpc
                    reorderPoint
                    reorderMax
                }}
                message
                }}
            }}
        ''')


def delete_product(product_id):
    return (f'''
            mutation{{
            deleteProduct(
                    id: {product_id}
            ){{
                success
            }}
            }}
    ''')


approve_product = '''
        mutation {{
            approveProduct(
            productId:{product_id}
            ){{
            product{{
                id
            }}
            success
            }}
        }}
    '''
set_price_string = '''
    mutation{{
        updatePrice(
            productIds:{product_ids} 
            salesPrice:{sales_price}
        ){{
            products{{
            id
            markup
            salesPrice
            }}
            errors
            message
        }}
    }}
'''

set_markup_string = '''
    mutation{{
        updatePrice(
            productIds:{product_ids} 
            markup:{markup}
        ){{
            products{{
            id
            markup
            salesPrice
            }}
            errors
            message
        }}
    }}
'''

set_nothing_string = '''
    mutation{{
        updatePrice(
            productIds:{product_ids} 
        ){{
            products{{
            id
            markup
            salesPrice
            }}
            errors
            message
        }}
    }}
'''

product_search_query = '''
query{{
    filterProducts(
        productName_Istartswith: "{search_term}"
        ){{
        edges {{
            node {{
            id
            productName
            tags
            globalUpc
            }}
        }}
    }}
}}
'''

product_filter_pagination_query = '''
query{{
    filterProducts(
        pageNumber: 1, pageCount: 1,
        productName_Istartswith: "{search_term}"
        ){{
        edges {{
            node {{
            id
            productName
            tags
            globalUpc
            }}
        }}
    }}
    totalProductsPagesCount
}}
'''

generalised_product_search_query = '''
query{{
    products(search: "{search_term}"){{
        id
        productName
        description
        brand
        skuNumber
        manufacturer
        productCategory{{
        id
        name
        }}
        preferredSupplier{{
        id
        name
        }}
    }}
}}
'''

update_loyalty_weight = '''
mutation{{
  updateLoyaltyWeight (productCategoryId:{product_category},
      loyaltyValue: {loyalty_value}
) {{
      category {{
    id
    name
    productSet {{
       edges {{
        node {{
          id
          productName
          loyaltyWeight
        }}
      }}
    }}
  }}
  }}
  }}
'''

update_a_product_loyalty_weight = '''
mutation{{
  productLoyaltyWeightUpdate (id:{product_id},
      loyaltyValue: {loyalty_value}
) {{
    product{{
      id
      productName
      loyaltyWeight
    }}
  }}
  }}
'''

proposed_edits_query = '''
query{
    proposedEdits {
        id
        productName
    }
}
'''

proposed_edit_query = '''
query{
    proposedEdit(id: 9) {
        id
        productName
    }
}
'''

product_query = '''
query{
    products {
        id
        productName
        isApproved
        globalUpc
    }
}
'''

near_expired_product_query = '''
query{
    nearExpiredProducts {
        id
        productName
    }
}
'''

create_product_category = '''
    mutation {{
    createProductCategory(
        name:"panadol",
        businessId: "{business_id}",
        isVatApplicable: true,
        loyaltyWeight: 1,
        markup: 20
        ){{
        productCategory{{
            id
            name
            isVatApplicable
            markup
        }}
        message
        }}
}}
    '''
create_product_category2 = '''
    mutation {{
    createProductCategory(
        name:"Paracetomal",
        isVatApplicable: false,
        loyaltyWeight: 1,
        markup: 1
        ){{
        productCategory{{
            id
            name
            isVatApplicable
            markup
        }}
        message
        }}
}}
    '''

edit_product_category = '''
    mutation {{
    editProductCategory(
      id:{id},
      name:"panadolextra"
    ){{
      productCategory{{
        id
        name
      }}
    message

    }}
}}

'''

delete_product_category = '''
    mutation{
    deleteProductCategory(
        id:7
    ){
    success
    }
    }

'''
create_measuremt_unit = '''
        mutation {
        createDispensingSize(
            name:"tablets"

        ){
        dispensingSize{
            id
            name
        }
        message

        }
    }


'''

edit_dispensing_size = '''
    mutation {
        editDispensingSize(
        id:6,
            name:"syrup"

        ){
        dispensingSize{
            id
            name
        }
        message

    }
}


'''


def deactivate_product(product_ids):
    return (f'''
            mutation {{
                deactivateProduct(productIds: {product_ids}){{
                    success
                }}
            }}
    ''')


def retrieve_deactivated_products(outlet_id):
    return (f'''
            query {{
                deactivatedProducts {{
                    id
                    productName
                }}
            }}
    ''')


def activate_product(product_ids):
    return (f'''
            mutation {{
                activateProduct(productIds: {product_ids}){{
                    success
                }}
            }}
    ''')


approve_proposed_edits = '''
    mutation {{
        approveProposedEdits(
        productId:{product_id}
        editRequestId:{edit_request_id}
        ){{
        product{{
        productName
        parent{{
            id
        }}
            isApproved
        }}
        message
        }}
    }}
'''

decline_proposed_edits = '''
mutation {{
    declineProposedEdits(
        productId:{product_id}
        editRequestId:{edit_request_id},
        comment:"Your edit request has not been accepted"
    ){{
    editRequest{{
    productName
    parent{{
        id
    }}
        isApproved
    }}
            message
    }}
}}
'''
all_products_default_pagination = '''
{
  products{
    id
    salesPrice
    productName
    manufacturer
  }
  totalProductsPagesCount
}
'''
all_proposed_products_default_pagination = '''
{
  proposedProducts{
    id
    salesPrice
    productName
    manufacturer
  }
  totalProductsPagesCount
}
'''
all_approved_products_default_pagination = '''
{
  approvedProducts{
    productName
    skuNumber
    tags
  }
  totalProductsPagesCount
}
'''
