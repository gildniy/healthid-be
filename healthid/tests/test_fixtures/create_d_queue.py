create_email_despatch = '''
mutation {{
  createEmailNotifications(
    recipientIds: "{recipient_ids}",
    subject: "Subject test",
    body: "subject testing testing"
  ){{
    queues {{
      status,
      recipient{{
        email
      }}
    }}
  }}
}}
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

create_email_despatch_with_due_date = '''mutation{{
  createEmailNotifications(
    recipientIds: "{recipient_ids}",
    dueDate: "{due_date}",
    subject: "Subject test",
    body: "subject testing testing"
  ){{
    queues{{
      status,
      recipient{{
        email
      }}
    }}
  }}
}}
'''
