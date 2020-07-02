def login_user(mobile_number, password):
    return (f'''
            mutation{{
                    loginUser(
                        mobileNumber: \"{mobile_number}\",
                        password: \"{password}\",
                        ){{
                            message
                            token
                        }}
            }}
            ''')


def login_user_email(email, password):
    return (f'''
            mutation{{
                    loginUser(
                        email: \"{email}\",
                        password: \"{password}\",
                        ){{
                            message
                            token
                        }}
            }}
            ''')
