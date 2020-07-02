from django.core.validators import MinValueValidator
from django.db import models

from healthid.models import BaseModel
from healthid.apps.products.models import BatchInfo
from healthid.apps.orders.models.orders import Order


class BarcodeScan(BaseModel):
    """ Hold data from a barcode scan.

    Attributes:
        scanned_number (str): The number scanned by the hardware
        order (:obj:`model`): The order this scan belongs to
        batch_info (:obj): `model`: The batch being scanned
        outlet (:obj): 'model': The outlet the batch belongs to
        count (int): How many items have been scanned
    """
    scanned_number = models.CharField(max_length=100)
    count = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    order = models.ForeignKey(Order, related_name='barcode_scans',
                              on_delete=models.CASCADE)
    batch_info = models.ForeignKey(BatchInfo, related_name='barcode_scans',
                                   on_delete=models.CASCADE)

    def __str__(self):
        """Return a string version of the model."""
        return f"Order NO: {self.order.order_number},\
                Scanned NO: {self.scanned_number}"
