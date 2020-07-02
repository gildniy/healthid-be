def create_register_query(outlet_id, number):
    return (f'''
                mutation{{
                createRegister(
                 name: "liver moore"
                 outletId:{outlet_id},
                 number: {number}
                 )
                   {{
                    registers{{name}}
                }}
            }}
            ''')


update_register_query = '''
mutation{{
  updateRegister (id:{register_id},
      name: "ever moore"
) {{
    message
    register {{
      name
    }}
    success
  }}
  }}
'''


def delete_register_query(register_id):
    return f'''mutation{{
                deleteRegister(id: {register_id}){{success}}
                    }}'''


def query_register(register_id):
    return (f'''query{{register(id: {register_id}){{id}}}}''')


registers_query = '''
        query{
            registers{
                id
                name
            }
        }
'''
