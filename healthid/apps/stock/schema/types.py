import graphene
from graphene_django import DjangoObjectType
from healthid.apps.stock.models import (
    StockTransfer, StockCountTemplate, StockCount, TransferBatch)


class TransferBatchType(DjangoObjectType):
    class Meta:
        model = TransferBatch


class StockTransferType(DjangoObjectType):
    class Meta:
        model = StockTransfer


class StockCountTemplateType(DjangoObjectType):
    class Meta:
        model = StockCountTemplate


class StockCountType(DjangoObjectType):
    class Meta:
        model = StockCount


class StockTransferAggregateType(graphene.ObjectType):
    product_name = graphene.String()
    product_sku_number = graphene.String()
    quantity_in_batches = graphene.String()
    quantity_sent = graphene.String()
    batches = graphene.String()