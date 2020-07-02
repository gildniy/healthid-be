import graphene
from graphene_django import DjangoObjectType
from graphene.utils.resolve_only_args import resolve_only_args
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.orders.schema.order_query import ProductBatchType
from healthid.apps.sales.models import (
    Sale, SaleDetail, SalesPrompt, SaleReturn, SaleReturnDetail, Payments)

from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.sales_responses import SALES_ERROR_RESPONSES


class SalesPromptType(DjangoObjectType):
    class Meta:
        model = SalesPrompt


class SaleDetailType(DjangoObjectType):
    batch = graphene.Field(ProductBatchType, source='get_batch')

    class Meta:
        model = SaleDetail

class PaymentsType(DjangoObjectType):
    class Meta:
        model = Payments

class SaleType(DjangoObjectType):
    register_id = graphene.Int(source='get_default_register')
    split_payments = graphene.List(PaymentsType)

    class Meta:
        model = Sale
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)

    def resolve_split_payments(self, info, **kwargs):
        return self.get_split_payments

    @resolve_only_args
    def resolve_id(self):
        return self.id


class ConsultationPaymentType(DjangoObjectType):

    class Meta:
        model = Sale


class SaleReturnType(DjangoObjectType):

    class Meta:
        model = SaleReturn


class SaleReturnDetailType(DjangoObjectType):
    class Meta:
        model = SaleReturnDetail


class Query(graphene.ObjectType):
    """
    Return a list of sales prompt.
    Or return a single sales prompt specified.
    """

    sales_prompts = graphene.List(SalesPromptType)
    sales_prompt = graphene.Field(SalesPromptType, id=graphene.Int())

    outlet_sales_history = graphene.List(SaleType,
                                         outlet_id=graphene.Int(required=True),
                                         search=graphene.String(),
                                         page_count=graphene.Int(),
                                         page_number=graphene.Int(),
                                         date_from=graphene.DateTime(),
                                         date_to=graphene.DateTime())
    all_sales_history = graphene.List(SaleType,
                                      page_count=graphene.Int(),
                                      page_number=graphene.Int())
    total_sales_pages_count = graphene.Int()
    total_number_of_sales = graphene.Int()

    sale_history = graphene.Field(
        SaleType, sale_id=graphene.Int(required=True))

    @login_required
    @user_permission('Manager')
    def resolve_sales_prompts(self, info, **kwargs):
        return SalesPrompt.objects.all()

    @login_required
    @user_permission('Manager')
    def resolve_sales_prompt(self, info, **kwargs):
        id = kwargs.get('id')
        sales_prompt = get_model_object(SalesPrompt, 'id', id)
        return sales_prompt

    @login_required
    def resolve_outlet_sales_history(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        search = kwargs.get('search')
        outlet_id = kwargs.get('outlet_id')
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')

        if date_to and not date_from:
            raise GraphQLError(SALES_ERROR_RESPONSES["provide_date_from"])

        sale = Sale()
        resolved_value = sale.sales_history(
            outlet_id=outlet_id,
            search=search,
            date_from=date_from,
            date_to=date_to)

        if page_count or page_number:
            sales = pagination_query(
                resolved_value, page_count, page_number)
            Query.pagination_result = sales
            return sales[0]

        if not resolved_value:
            return GraphQLError(SALES_ERROR_RESPONSES["no_sales_error"])

        return resolved_value

    @login_required
    def resolve_total_sales_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying, totalSalesPagesCount query field should
        strictly be called after the sales query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_total_number_of_sales(self, info, **kwargs):
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_sale_history(self, info, sale_id):
        sale = get_model_object(Sale, 'id', sale_id)
        return sale

    @login_required
    @user_permission('Manager')
    def resolve_all_sales_history(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')

        resolved_value = Sale.objects.all()

        if page_count or page_number:
            sales = pagination_query(
                resolved_value, page_count, page_number)
            Query.pagination_result = sales
            return sales[0]
        if resolved_value:
            paginated_response = pagination_query(resolved_value,
                                                  PAGINATION_DEFAULT[
                                                      "page_count"],
                                                  PAGINATION_DEFAULT[
                                                      "page_number"])

            Query.pagination_result = paginated_response
            return paginated_response[0]
        return GraphQLError(SALES_ERROR_RESPONSES["no_sales_error"])
