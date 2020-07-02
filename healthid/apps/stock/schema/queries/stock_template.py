import graphene
from graphql_jwt.decorators import login_required

from healthid.apps.stock.models import StockCountTemplate
from healthid.apps.stock.schema.types import StockCountTemplateType


class StockTemplateQuery(graphene.ObjectType):
    stock_templates = graphene.List(
        StockCountTemplateType,
        outlet_id=graphene.Int(required=True))
    stock_template = graphene.Field(
        StockCountTemplateType,
        template_id=graphene.Int(required=True),
        outlet_id=graphene.Int(required=True)
    )

    @login_required
    def resolve_stock_templates(self, info, **kwargs):
        outlet_id = kwargs.get('outlet_id')
        return StockCountTemplate.objects.filter(outlet_id=outlet_id)

    @login_required
    def resolve_stock_template(self, info, **kwargs):
        template_id = kwargs.get('template_id')
        outlet_id = kwargs.get('outlet_id')
        return StockCountTemplate.objects.filter(
            outlet_id=outlet_id, id=template_id).first()
