register_user_query = '''
            mutation {{
               createUser(
                   email:"{email}",
                   mobileNumber:"{mobileNumber}",
                   password:"{password}",
               ) {{
                 errors
                 success
                 verificationLink
               }}
            }}
            '''

login_user_query = '''
        mutation GetToken {{
            tokenAuth(
              email: "{email}",
              password: "{password}"
              ){{
              token
              }}
            }}
        '''

update_username_query = '''
          mutation {{
            updateUser(
              username: "{}"
            ){{
              error
              success
              user{{
              id
              username
              }}
            }}
          }}
        '''

update_email_query = '''
          mutation {{
            updateUser(
              email: "{}"
            ){{
              error
              success
              user{{
              id
              email
              }}
            }}
          }}
        '''

update_image_query = '''
          mutation {{
            updateUser(
              profileImage: "{}"
            ){{
              error
              success
              user{{
              id
              profileImage
              }}
            }}
          }}
        '''

add_user_query = '''
mutation {{
        addUser (
          email:"{email}",
          outletId: ["{outletId}"],
          roleId: "{roleId}",
          mobileNumber:"{mobileNumber}",
          firstName: "Firstname",
          lastName: "Lastname",
          username: "username",
          startingDate: "2019-12-04",
          birthday: "2019-11-15"
        ){{
          user{{
            email
          mobileNumber
          }}
        success
        errors
        }}
      }}
  '''

admin_update_user_query = '''
mutation {{
        adminUpdateUser (
        id:"{id}",
        jobTitle: "{jobTitle}",
        email:"{email}",
        mobileNumber:"{mobileNumber}",
        firstName: "{firstname}",
        lastName: "Lastname",
        username: "newUsername",
        startingDate: "2019-12-10",
        birthday: "2019-11-15"
      ) {{
        errors
        message
        user {{
          id
          firstName
          email
          mobileNumber
          jobTitle
        }}
      }}
      }}
  '''

update_user_role_query = '''
mutation updateRole {{
           updateRole (roleId:"{roleId}",
           userId:"{userId}"){{
           errors
            user {{
              id
              email
              role {{
                name
              }}
            }}
          }}
        }}
'''

add_user_business_query = '''
    mutation addUserBusiness {{
    addUserBusiness (userId:"{userId}", businessId:"{businessId}") {{
        errors
        message
        user {{
          id
          email
        }}
      }}
    }}
'''

password_reset_query = '''
  mutation {{
    resetPassword(email: "{email}"){{
      success
      resetLink
    }}
  }}
'''

password_reset_json = '''
  {{
    "user": {{
      "password": "{password}"
      }}
  }}
'''


user = {
    'email': "arkafuuma@gmail.com",
    'mobileNumber': "+256788088831",
    'password': "Password@1"
}

user_query = '''
  query{
    me{
      id
      email
    }
  }
'''

users_query = '''
  query{
    users{
      id
      email
    }
  }
'''

create_role = """
            mutation createRole {{
               createRole(input: {{
                 name: "{name}"
               }}) {{
                 success
                 role {{
                   name
                 }}
               }}
            }}
                """

get_role_by_id = """
        query {{
          role(id:"{id}") {{
            id
            name
          }}
        }}
        """

get_role_by_name = """
        query {{
          role(name:"{name}") {{
            id
            name
          }}
        }}
        """

get_roles = """
        query {
          roles{
            id
            name
          }
        }
        """

edit_role = """
            mutation editRole {{
           editRole (id:"{id}", input:{{
              name:"Test Role"
          }}) {{
            success
            role {{
              name
            }}
          }}
        }}

        """
create_role_with_empty_name = """
            mutation createRole {
               createRole(input: {
                 name: ""
               }) {
                 success
                 role {
                   name
                 }
               }
            }
                """
