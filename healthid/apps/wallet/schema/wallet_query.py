import graphene
from graphql_jwt.decorators import login_required
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT
from healthid.apps.wallet.schema.wallet_schema import CustomerCreditType
from healthid.apps.wallet.models import CustomerCredit
from healthid.utils.app_utils.database import get_model_object


class CustomerCreditQuery(graphene.ObjectType):
    """ Queries Customer Credit wallet. """

    customer_credits = graphene.List(CustomerCreditType,
                                     page_count=graphene.Int(),
                                     page_number=graphene.Int(),)
    customer_credit = graphene.Field(
        CustomerCreditType,
        customer_id=graphene.Int(),
    )
    total_customer_credit_account_pages = graphene.Int()
    pagination_result = None
    @login_required
    def resolve_customer_credits(self, info, **kwargs):

        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        resolved_values = CustomerCredit.objects.all()
        if page_count or page_number:
            customer_credits = pagination_query(
                resolved_values, page_count, page_number
            )

            CustomerCreditQuery.pagination_result = customer_credits
            return customer_credits[0]

        paginated_response = pagination_query(
            resolved_values,
            PAGINATION_DEFAULT['page_count'],
            PAGINATION_DEFAULT['page_number'])
        CustomerCreditQuery.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_customer_credit(self, info, **kwargs):
        customer_id = kwargs.get('customer_id')
        wallet = get_model_object(
            CustomerCredit, 'customer_id', customer_id)
        return wallet

    @login_required
    def resolve_total_customer_credit_account_pages(self, info, **kwargs):
        """ Resolves the total number of pages on paginated store credits. """
        if not CustomerCreditQuery.pagination_result:
            return 0
        return CustomerCreditQuery.pagination_result[1]
