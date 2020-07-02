from django.db import models
from healthid.apps.authentication.models import User
from healthid.models import BaseModel
import datetime
from django.utils import timezone
from healthid.utils.app_utils.id_generator import id_gen


class DespatchQueue(BaseModel):
    '''
    Model class to handle despatch queue
    '''

    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

    SEND_STATUSES = (
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (SENT, "Sent"),
        (FAILED, "Failed"),
        (CANCELLED, "Cancelled")
    )

    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    ) 
    despatch_type = models.CharField(max_length=10, default='EMAIL')
    recipient = models.ForeignKey(User, related_name="recipient",
                                  on_delete=models.CASCADE)
    due_date = models.DateTimeField(verbose_name='DateTime', null=True)
    status = models.CharField(max_length=10, choices=SEND_STATUSES,
                              default=PENDING)

    @property
    def add_due_date(self):
        if self.due_date is None:
            dt = timezone.now()
            self.due_date = dt - \
                datetime.timedelta(microseconds=dt.microsecond)
        return self.due_date


class Despatch_Meta(BaseModel):
    '''Model to handle all notifications
    '''
    dataKey = models.TextField(max_length=255, null=False)
    dataValue = models.TextField(null=False)
    despatch = models.ForeignKey(DespatchQueue,
                                 related_name='despatch',
                                 on_delete=models.CASCADE)

    class Meta:
        unique_together = (("despatch", "dataKey"))
        indexes = [
            models.Index(fields=['dataKey'])
        ]
