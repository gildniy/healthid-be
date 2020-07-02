from django.db import models
from healthid.apps.profiles.models import Profile


class CustomerMeta(models.Model):
    """
    This model is for product meta data
    Attributes:
        dataKey(string): key of the value
        dataValue(string): Exact value of a key
        Profile: foreign key from Profile
    """
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    dataKey = models.CharField(max_length=100, null=True)
    dataValue = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = (("customer", "dataKey"))

    def __int__(self):
        return self.id
