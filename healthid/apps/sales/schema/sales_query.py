import graphene
from django.db.models import Q
from graphql_jwt.decorators import login_required
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql.error import GraphQLError
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT
from healthid.utils.app_utils.pagination import pagination_query

from healthid.apps.sales.sales_velocity import SalesVelocity
from healthid.apps.sales.models import BatchHistory, SalesPerformance
from healthid.utils.app_utils.get_user_business import get_user_business
from healthid.utils.app_utils.pagination import pagination_query


class Velocity(graphene.ObjectType):
    default_sales_velocity = graphene.Float()
    calculated_sales_velocity = graphene.Float()
    message = graphene.String()


class BatchHistoryType(DjangoObjectType):
    class Meta:
        model = BatchHistory
    
    totalProductsSold = graphene.Int()
    totalQtySold = graphene.Int()
    totalCashAmount = graphene.Float()
    totalCardAmount = graphene.Float()


class SalePerformanceType(DjangoObjectType):
    class Meta:
        model = SalesPerformance

        filter_fields = {
            'discount': ['exact'],
            'subtotal': ['exact'],
            'cashier__first_name': ['exact'],
            'cashier__last_name': ['exact'],
            'created_at': ['lt', 'gt', 'exact'],
            'transaction_date': ['lt', 'gt', 'exact'],
            'customer__first_name': ['exact'],
            'customer__last_name': ['exact'],
        }
        interfaces = (graphene.relay.Node, )


class Query(graphene.ObjectType):
    """
    Queries Sales
    Args:
        product_id (int) the product id
        outlet_id (int) the outlet id
    returns:
        Two float values for the calculated sales velocity
            and the default sales velocity
    """

    sales_velocity = graphene.Field(
        Velocity,
        product_id=graphene.Int(),
        outlet_id=graphene.Int())

    team_report = graphene.List(
        BatchHistoryType,
        date_from=graphene.DateTime(required=True),
        date_to=graphene.DateTime(required=True),
        page_count=graphene.Int(),
        page_number=graphene.Int())
    sales = graphene.relay.Node.Field(SalePerformanceType)
    sale_performances = DjangoFilterConnectionField(
            SalePerformanceType,
            page_count=graphene.Int(),
            page_number=graphene.Int(),
            period=graphene.String(),
            outlets=graphene.List(graphene.Int)
        )

    @login_required
    def resolve_sales_velocity(self, info, **kwargs):
        product_id = kwargs.get('product_id')
        outlet_id = kwargs.get('outlet_id')

        return SalesVelocity(
            product_id=product_id,
            outlet_id=outlet_id).velocity_calculator()
            
    @login_required
    def resolve_team_report(self, info, **kwargs):

        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        
        business = get_user_business(info.context.user)
        resolved_sales = BatchHistory.team_performance(self, business, date_from, date_to)

        if page_number and page_count:
            sales = pagination_query(resolved_sales, page_count, page_number)
            Query.pagination_result = sales

            return sales[0]

        return resolved_sales

    def resolve_sale_performances(self, info, **kwargs):

        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        period = kwargs.get('period')
        outlets = kwargs.get('outlets')
        period_possible_values = ['day', 'week', 'month']

        if period and period not in period_possible_values:
            raise GraphQLError(f"Invalid Argument: period = {period} ")

        kwargs.pop('page_count', None)
        kwargs.pop('page_number', None)
        kwargs.pop('period', None)
        kwargs.pop('outlets', None)

        if outlets:
            resolve_sales = SalesPerformance.objects.filter(
                Q(**kwargs) & Q(outlet_id__in = outlets)
                )
        else:
            resolve_sales = SalesPerformance.objects.filter()
        

        if not resolve_sales:
            raise GraphQLError('No Data available')

        if page_count and page_number:
            filtered_sales = pagination_query(resolve_sales, page_count, page_number)
            Query.pagination_result = filtered_sales
            return filtered_sales[0]

        return resolve_sales