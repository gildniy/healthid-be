
consultations = '''
  query{{consultation(id:{id}){{
    id
    consultationName
  }}
  }}
'''

create_consultation_item = '''mutation {{
                createConsultationItem(
                    consultationName:"{consultation_name}",
                    description:"{description}",
                    consultantRole:"{consultant_role}",
                    approvedDeliveryFormats:["{approved_formats}"],
                    businessId:"{business_id}",
                    minutesPerSession:{minutes_per_session},
                    pricePerSession:{price_per_session}
                  ){{
                    consultation{{
                      id
                      description
                      consultationName
                    business{{
                        id
                      }}
                  }}
                  success
                  }}
                  }}
                  '''


edit_consultation_item = '''mutation {{
                editConsultationItem(
                    consultationId:{consultation_id},
                    description:"{description}"
                  ){{
                    consultation{{
                      id
                      description
                      consultationName
                    business{{
                        id
                      }}
                  }}
                  message
                  }}
                  }}
                  '''

delete_consultation_item = '''mutation{{
                    deleteConsultationItem(
                      id:{id}
                      ){{
                        message
                        }}
                        }}
                        '''

book_consultation = '''mutation{{
                bookConsultation(
                  customerId: {customer_id},
                  consultationTypeId: {consultation_type_id},
                  status: "{status}",
                  outletId: {outlet_id}
                ){{
                  bookConsultation{{
                    id
                    bookingDate
                    status
                    consultationType{{
                      consultationName
                    }}
                    outlet{{
                      id
                      name
                    }}
                    customer{{
                      id
                      firstName
                      lastName
                    }}
                    bookedBy{{
                      email
                    }}
                    event{{
                      eventType{{
                        name
                      }}
                      startDate
                      startTime
                    }}
                  }}
                  success
                }}
              }}
              '''

update_consultation = '''mutation{{
                updateConsultation(
                  consultationId: {consultation_id}
                  status: "{status}"
                ){{
                  updateConsultation{{
                    id
                    bookingDate
                    status
                    consultationType{{
                      consultationName
                    }}
                    outlet{{
                      id
                      name
                    }}
                    customer{{
                      id
                      firstName
                      lastName
                    }}
                    bookedBy{{
                      email
                      username
                    }}
                    event{{
                      eventType{{
                        id
                        name
                      }}
                      eventTitle
                    }}
                  }}
                  success
                }}
                }}
                '''

delete_consultation = '''mutation {{
            deleteBookedConsultation(
              id: {consultation_id}
            ){{
            message
          }}
          }}
          '''

add_medical_notes = '''mutation{{
            addMedicalNotes(
              consultationId: {consultation_id},
              author: "{consultant_name}"
              medicalNotes: "{medical_notes}"
            ){{addNotes{{
              id
              consultation{{
                id,
                customer{{
                  id
                  firstName
                  lastName
                }}
                consultationType{{
                  id,
                  consultationName
                }}
                status
                medicalhistorySet{{
                  medicalNotes,
                  author,
                  createdAt
                }}
              }}
            }}
            }}
          }}
'''

book = '''mutation{{
  bookConsultation(
    customerId: {customer_id},
    consultationTypeId: {consultation_type_id},
    status: "{status}"
    ){{
    bookConsultation{
      bookingDate,
      status,
      consultant
    }}
}}
'''
