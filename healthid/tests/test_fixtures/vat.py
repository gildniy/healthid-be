
def set_vat(preference_id):
    return (f'''
            mutation{{
                updatePreference(
                    outletCurrency:"Euro"
                    preferenceId:\"{preference_id}\"
                    outletVat:29
                ){{
                    success
                }}
                }}
                ''')


query_vat_by_id = '''
query{
    vat(id: "t1234qwe"){
        id
        rate

    }
    success
}
'''
query_vat_by_wrong_id = '''
query{
    vat(id: "t1234qwe444"){
        id
        rate

    }
    success
}
'''
