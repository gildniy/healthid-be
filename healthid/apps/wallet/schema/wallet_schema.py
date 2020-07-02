from graphene_django import DjangoObjectType
from healthid.apps.wallet.models import (
    CustomerCredit, StoreCreditWalletHistory)


class CustomerCreditType(DjangoObjectType):
    class Meta:
        model = CustomerCredit


class CustomerCreditHistoryType(DjangoObjectType):
    class Meta:
        model = StoreCreditWalletHistory
