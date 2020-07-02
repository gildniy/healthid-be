register_user_query = '''
                mutation{{
                    createUser(
                    email:"{email}",
                    mobileNumber:"{mobileNumber}",
                    password:"{password}",
                ) {{
                    errors
                    success
                }}
                }}
                '''


login_user_query = '''
            mutation {
               createUser(
                   email:"user@gmail.com",
                   mobileNumber:"+256770777777",
                   password:"Passsword12"
               ) {
                 success
               }
            }
            '''


login_mutation = '''
            mutation GetToken($email: String!, $password: String!){
                tokenAuth(email: $email, password: $password) {
                token
                user {
                    id
                }
                }
            }
            '''

loginUser_mutation = '''
            mutation {{
                loginUser(
                    email: "{email}",
                    password: "{password}",
                ){{
                restToken
                }}
            }}
            '''


test_users_query = '''
            {
                users {
                    id
                }
            }
            '''


query_str = '''
      mutation{{
          updateAdminUser(
              firstName:"{firstname}",
              lastName:"{lastname}",
              username:"{username}",
              email:"{email}",
              secondaryEmail:"{email}",
              mobileNumber:"{mobile_number}",
              secondaryPhoneNumber:"{mobile_number}",
              ){{
              user{{
                  firstName
                  lastName
                  username
                  secondaryEmail
              }},
              success
          }}
      }}
      '''
