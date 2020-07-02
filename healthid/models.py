from django.db import models
from django.utils import timezone

from healthid.apps.authentication.models import User
from healthid.manager import BaseManager


class BaseModel(models.Model):
    """
    General model to implement common fields and soft delete

    Attributes:
        created_at: Holds date/time for when an object was created.
        updated_at: Holds date/time for last update on an object.
        deleted_at: Holds date/time for soft-deleted objects.
        deleted_at: Holds user who soft-deleted an objects.
        objects: Return objects that have not been soft-deleted.
        all_objects: Return all objects(soft-deleted inclusive)
    """
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    objects = BaseManager()
    all_objects = BaseManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self, user=None):
        self.deleted_at = timezone.now()
        if user is not None:
            self.deleted_by = user
        self.save()

    def hard_delete(self):
        super(BaseModel, self).delete()
