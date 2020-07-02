create_consultations = '''
    mutation {{
        createConsultationItem (
        consultationName:"Bone marrow",
        description:"would like to seek medical advise regarding bone marrow",
        businessId:"{business_id}",
        approvedDeliveryFormats:["In_Person"],
        consultantRole:"Doctor",
        minutesPerSession: 10,
        pricePerSession:30000
        ){{
        consultation{{
            id
            description
            consultationName
        business{{
            tradingName
            }}
        }}
        success
    }}
    }}
'''

retrieve_consultations = '''
query {
  consultations{
        id
        description
        consultationName
       business{
          tradingName
        }
  }
  totalConsultationsPagesCount
}
'''
retrieve_paginated_consultations = '''
query {
  consultations(pageCount:1, pageNumber:1) {
        id
        description
        consultationName
       business{
          tradingName
        }
  }
  totalConsultationsPagesCount
}
'''
retrieve_consultation = '''
query {{
  consultation(consultationId: {consultation_id}) {{
        id
        description
        consultationName
       business{{
          tradingName
        }}
    }}
}}
'''

consultation_id_query = '''
    query {{consultation(consultationId: {consultation_id}){{
        id
        description
        consultationName
        business{{
            tradingName
            }}
    }}
    }}
'''

retrieve_schedule_consultations = '''
    query {
      bookings {
        bookingDate
        status
        consultant
        id
        bookedBy{
          lastName
          firstName
          profileImage
          email
        }
        outlet{
          id
        }
      }
    }
  '''
retrieve_booking = '''
  query {{
  booking (id: {id}) {{
    bookingDate
    status
    consultant
    bookedBy{{
      lastName
      firstName
      profileImage
      email
    }}
    id
  }}
}}
'''

book_consultation = '''
mutation {{
    bookConsultation(
    customerId:{}
    consultationTypeId:{}
    outletId:{}
    consultant:"Consultant"
    status:"Now"
    bookingDate:"{}"
    ){{
      bookConsultation {{
        status
      }}
    }}
}}
'''

update_consultation = '''
mutation {{
  updateConsultation(
  consultationId:{}
  bookingDate:"{}"
  ) {{
    updateConsultation {{
      status
      paid
    }}
  }}
}}
'''


delete_booked_consultation = '''
mutation{{
  deleteBookedConsultation(
    id:{id}
  ) {{
    message
  }}
}}
'''

query_all_bookings = '''
  query {
    bookings {
      bookingDate
      status
    }
  }
'''

query_all_paginated_bookings = '''
  query {
    bookings(pageNumber:1,pageCount:1) {
      bookingDate
      status
    }
    totalBookingsPagesCount
  }
'''

edit_consultation_item = '''
mutation {{
  editConsultationItem(
      consultationId:{},
        description:"Consultation Description",
  ) {{
    consultation {{
      id
    }}
  }}
}}

'''

delete_consultation_item = '''
mutation {{
  deleteConsultationItem(id:{}) {{
    message
  }}
}}

'''


add_medical_notes = '''
mutation{{
  addMedicalNotes(
    consultationId:{},
    author:"Authorname",
    medicalNotes:"{}"
  ) {{
    addNotes {{
      medicalNotes
    }}
  }}
}}
'''
