from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from healthid.apps.authentication.models import User
from healthid.apps.events.models import Event
from healthid.apps.profiles.models import Profile
from healthid.apps.sales.models import Sale
from healthid.models import BaseModel
from healthid.apps.outlets.models import Outlet
from healthid.apps.business.models import Business
from healthid.utils.messages.consultation_reponses import\
    CONSULTATION_ERROR_RESPONSES


class ConsultationCatalogue(BaseModel):
    """
    A model for saving data on consultations that
    a business offers
    """
    DOCTOR, NURSE, HEALTH_COACH, PHARMACIST, SALES_ASSOCIATE =\
        'Doctor', 'Nurse', 'Health_Coach', 'Pharmacist', 'Sales_Person'
    CONSULTANT_TYPES = [
        (DOCTOR, 'Doctor'),
        (NURSE, 'Nurse'),
        (HEALTH_COACH, 'Health Coach'),
        (PHARMACIST, 'Pharmacist'),
        (SALES_ASSOCIATE, 'Sales Associate')]

    IN_PERSON, TELEPHONIC, VIDEO_CONFERENCING =\
        'In_Person', 'Telephonic', 'Video_Conferencing'
    DELIVERY_FORMATS = [
        (IN_PERSON, 'In Person'),
        (TELEPHONIC, 'Telephonic'),
        (VIDEO_CONFERENCING, 'Video Conferencing'),
    ]

    consultation_name = models.CharField(max_length=80)
    description = models.TextField()
    business = models.ForeignKey(
        Business, related_name='consultation_catalogue',
        on_delete=models.CASCADE,
        null=True)
    approved_delivery_formats = ArrayField(
        models.CharField(
            choices=DELIVERY_FORMATS, default=IN_PERSON, max_length=50))
    consultant_role = models.CharField(
        choices=CONSULTANT_TYPES, max_length=20, default=PHARMACIST)
    minutes_per_session = models.IntegerField()
    price_per_session = models.IntegerField()

    class Meta:
        unique_together = ((
            'consultation_name', 'business', 'approved_delivery_formats',
            'minutes_per_session'))

    def save(self, *args, **kwargs):
        self.clean_fields(exclude='deleted_by')
        super().save(*args, **kwargs)

    @property
    def get_consultant_role(self):
        return self.get_consultant_role_display()


class CustomerConsultation(BaseModel):
    """
    A model for saving data on consultations
    a customer has booked
    """
    NOW, DONE, LATER = 'Now', 'Done', 'Later'
    STATUS_TYPES = [
        (NOW, "Now"),
        (DONE, 'Already Completed'),
        (LATER, 'Later'),
    ]

    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    consultation_type = models.ForeignKey(
        ConsultationCatalogue, on_delete=models.SET_NULL, null=True,
        related_name='customer_consultations')
    consultant = models.CharField(max_length=50, blank=True)
    status = models.CharField(choices=STATUS_TYPES, max_length=10, default=NOW)
    booking_date = models.DateTimeField(default=timezone.now)
    booked_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='booked_by_user')
    paid = models.BooleanField(default=False)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='user_consultation_updates')
    sale_record = models.OneToOneField(
        Sale, on_delete=models.SET_NULL, null=True,
        related_name='consultation_sale_record')
    event = models.OneToOneField(
        Event, on_delete=models.SET_NULL, null=True,
        related_name='consultation_event')
    outlet = models.ForeignKey(
        Outlet, on_delete=models.CASCADE,
        related_name='outlet_consultations',
        null=True)

    def save(self, *args, **kwargs):
        """
        Overrides custom save method to include business
        logic
        """
        if self.paid and not self.sale_record:
            raise ValidationError(
                CONSULTATION_ERROR_RESPONSES["paid_status_error"])
        if self.booking_date.date() < timezone.now().date():
            raise ValidationError(
                CONSULTATION_ERROR_RESPONSES['booking_date_error'])

        self.clean_fields(
            exclude='deleted_by, sale_record, updated_by, event,\
            consultation_type')
        super().save(*args, **kwargs)

    @property
    def medical_history(self):
        """
        Returns the medical notes for a particular consultation session.
        This is important as notes may be updated by different consultants
        and a record of this information is needed by the user.
        """
        return MedicalHistory.objects.filter(
            consultation=self).values(
            'updated_at', 'medical_notes', 'author')

    @property
    def end_time(self):
        """
        Calculates when a consultation is expected to end based on the
        consultation item's minutes per session
        """
        return self.booking_date + timedelta(
            minutes=self.consultation_type.minutes_per_session)

    @property
    def get_status(self):
        return self.get_status_display()


class MedicalHistory(BaseModel):
    """
    A model that stores a customer's medical history
    """
    consultation = models.ForeignKey(
        CustomerConsultation, on_delete=models.CASCADE)
    medical_notes = models.TextField()
    author = models.CharField(max_length=50, blank=True)
    authorized_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='user_authorizations')

    def save(self, *args, **kwargs):
        """
        Overrides the model.save() method to ensure that consultations
        marked as complete cannot have medical notes added to them
        """
        if self.consultation.status == 1:
            raise ValidationError(
                CONSULTATION_ERROR_RESPONSES['completed_status_error'])
        super().save(*args, **kwargs)
