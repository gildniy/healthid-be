import graphene
from healthid.apps.stock.schema.queries.stock_count \
    import StockCountQuery
from healthid.apps.stock.schema.queries.stock_template \
    import StockTemplateQuery
from healthid.apps.stock.schema.queries.stock_transfer \
    import StockTransferQuery


class Query(
    StockTemplateQuery,
    StockCountQuery,
    StockTransferQuery,
    graphene.ObjectType
):
    pass
