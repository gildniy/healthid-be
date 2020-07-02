
def set_currency(preference_id):
    return (f'''
            mutation{{
                updatePreference(
                    outletCurrency:"Euro"
                    preferenceId:\"{preference_id}\"
                ){{
                    success
                }}
                }}
                ''')


def set_existing_currency(preference_id):
    return (f'''
            mutation{{
                updatePreference(
                    outletCurrency:"Euro"
                    preferenceId:\"{preference_id}\"
                ){{
                    success
                }}
                }}
                ''')


def get_wrong_currency():
    return (f'''
                query{{
                    currency(name: "Mozambicann Metical"){{
                        id
                        name
                        symbol
                        symbolNative
                        decimalDigits
                        rounding
                        code
                        namePlural
                    }}
                    }}
            ''')


def get_currencies():
    return (f'''
            query{{
                currencies{{
                    name
                    symbol
                    symbolNative
                    decimalDigits
                    rounding
                    code
                    namePlural
                }}
                }}
        ''')


def get_currency():
    return (f'''
            query{{
                currency(name: "Mozambican Metical"){{
                    id
                    name
                    namePlural
                    decimalDigits
                }}
                }}
            ''')
