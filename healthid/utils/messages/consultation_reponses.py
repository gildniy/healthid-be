CONSULTATION_SUCCESS_RESPONSES = {
    "consultation_schedule_success": "Consultation has been scheduled",
    "delete_booking": "Consultation for {} deleted successfully"
}

CONSULTATION_ERROR_RESPONSES = {
    "empty_field_error": "The {} field can't be empty",
    "duplicate_consultation_error": "Consultation with "
                                    "consultation_name {}, already exists",
    "inexistent_outlet": "Outlet with id {} does not exist",
    "booking_date_error":
    "Booking date cannot be earlier than present date and time",
    "paid_status_error":
    "Consultation cannot be marked as paid if it does not have \
     a sale record attached to it",
    "completed_status_error": "Consultation is already marked as complete",
    "consultation_doesnot_exist_error":
    "Consultation does not exist in your business",
    "schedule_error": "Consultation Schedule doesnot belong  in your outlet",
    "invalid_id": "The id {} should be a positive number",
    "outlet_error": "outlet must be part of the business where the consulation \
    was created",
    "no_scheduled_consultations": "Your outlet has no scheduled consultations."
}
