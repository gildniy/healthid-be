def create_outlet(business_id, type_id, country, city):
    return (f'''
            mutation{{
                createOutlet(
                    businessId: \"{business_id}\",
                    kindId: {type_id},
                    name: "green ville",
                    addressLine1: "10/11 Nagera",
                    addressLine2: "Nakawa, Kampala",
                    lga: "Nakawa",
                    country: "{country}",
                    cityName: "{city}",
                    phoneNumber: "+2567803201607",
                    dateLaunched: "2019-02-27",)
                   {{
                    outlet{{name, id}}
                }}
            }}
            ''')


def update_outlet(outlet_id, outlet_name, country, city):
    return (f'''
            mutation{{
                updateOutlet(
                    id: {outlet_id},
                    name: "{outlet_name}",
                    addressLine1: "10/11 Nagera",
                    addressLine2: "Nakawa, Kampala",
                    country: "{country}",
                    cityName: "{city}",
                    lga: "Nakawa",
                    phoneNumber: "+2567803201607",
                    dateLaunched: "2019-02-27",)
                   {{
                    outlet{{name}}
                }}
            }}
            ''')


def delete_outlet(outlet_id):
    return f'mutation{{deleteOutlet(id: {outlet_id}){{success}}}}'


query_outlets_string = '''
    query{
      outlets{
      name
      id,
      taxNumber
    }
  }
'''

create_outlet_string = '''
  mutation{{
      createOutlet(
          businessId: \"{business_id}\",
          kindId: {type_id},
          name: "{outlet_name}",
          addressLine1: "10/11 Nagera",
          addressLine2: "Nakawa, Kampala",
          lga: "Nakawa",
          country: "nigeria",
          cityName: "lagos",
          phoneNumber: "+2567803201607",
          dateLaunched: "2019-02-27",
          taxNumber: "{tax_number}"
          )
          {{
          outlet{{name, id}}
      }}
  }}
'''
create_country_string = '''
            mutation{{
            createCountry(name:"{country_name}"){{
                country{{
                name
                id
                citySet{{
                    id
                    name
                }}
                }}
            }}
            }}
        '''

update_country_string = '''
        mutation{{
        editCountry(id:{id}, name:"{name}"){{
            country{{
            name
            id
            }}
            success
        }}
    }}
'''

delete_country_string = '''
        mutation{{
        deleteCountry(id:{id}){{
            success
            }}
        }}
'''

query_countries_string = '''
        query{
        countries{
            id
            name
          }
        }
    '''


query_country_string_with_name = '''

        query{{
        country(name:"{name}"){{
            id
            name
         }}
        }}
'''


query_country_string_with_id = '''

        query{{
        country(id:{id}){{
            id
            name
         }}
        }}
    '''

create_city_string = '''

        mutation{{
        createCity(countryId:{country_id}, cityName:"{city_name}"){{
                city{{
            id
            name
            }}
        }}
        }}
    '''
edit_city_string = '''

        mutation{{
        editCity(id:{id}, name:"{name}"){{
            city{{
                id
                name
            }}
            success
        }}
    }}
'''

query_city_string_by_name = '''

    query{{
        city(name:"{name}"){{
            id
            name
        }}
    }}
'''

query_city_string_by_id = '''

    query{{
        city(id:{id}){{
            id
            name
        }}
    }}
'''
query_cities_string = '''
    query{
    cities{
        id
        name
    }
}
'''

activate_deactivate_outlet_user = '''
mutation {{
    activateDeactivateOutletUser(
        userId: "{user_id}",
        outletId: {outlet_id},
        isActive: {is_active}
        ){{
            message
        }}
}}
'''
