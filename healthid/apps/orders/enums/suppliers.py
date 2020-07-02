from enum import Enum


class PaymentTermsType(Enum):
    ON_CREDIT = "on credit"
    CASH_ON_DELIVERY = "cash on delivery"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
