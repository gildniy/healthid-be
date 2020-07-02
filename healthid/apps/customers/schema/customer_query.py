from django.core.validators import RegexValidator, EmailValidator
from django.db.models import Q
from healthid.apps.business.models import Business
from healthid.utils.app_utils.get_user_business import get_user_business
import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django import DjangoObjectType
from graphene.utils.resolve_only_args import resolve_only_args
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from healthid.apps.profiles.models import Profile
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.customer_responses import CUSTOMER_ERROR_RESPONSES
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT


class CustomerCustomerType(DjangoObjectType):
    class Meta:
        model = Profile
        filter_fields = {
            'id': ['exact'],
            'first_name': ['iexact', 'icontains', 'istartswith'],
            'last_name': ['iexact', 'icontains', 'istartswith'],
            'primary_mobile_number': ['exact'],
            'secondary_mobile_number': ['exact'],
            'email': ['iexact'],
            'city_id': ['exact'],
            'local_government_area': ['iexact'],
            'loyalty_member': ['exact']
        }

        interfaces = (graphene.relay.Node, )

    id = graphene.ID(required=True)

    @resolve_only_args
    def resolve_id(self):
        return self.id


class Query(graphene.AbstractType):
    """
    Queries Customer
    Args:
        name (str) any of the customer's name
        mobile_number (str) any of the customers mobile number
        # Arguments when filtering
        customer_id (str) the customer's unique identifier
        first_name (str) the customer's first name
        last_name (str) the customer's last name
        primary_mobile_number (str) the customer's primary mobile number
        secondary_mobile_number (str) the customer's secondary mobile number
        email (email) the customers email
        local_government_area (str) the customers lga
        city_id (int) foreign key, city of the customer
        loyalty_member (bool)
    returns:
         customer(s) object where one or more results were found,
         otherwise a GraphqlError is raised
         In the case parameters for pagination are provided the,
         paginated response is returned based on the pagination params
    """

    customers = graphene.List(
        CustomerCustomerType, page_count=graphene.Int(),
        page_number=graphene.Int(),
        offline=graphene.Boolean()
        )
    customer = graphene.Field(
        lambda: graphene.List(
            CustomerCustomerType),
        search=graphene.String(),
        name=graphene.String(),
        mobile_number=graphene.String(),
        customer_id=graphene.String())
    filter_customers = DjangoFilterConnectionField(
        CustomerCustomerType,
        page_count=graphene.Int(),
        page_number=graphene.Int())
    total_customers_pages_count = graphene.Int()
    total_customers_count = graphene.Int()
    pagination_result = None

    @login_required
    def resolve_customers(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        offline = kwargs.get('offline')

        business_id = get_user_business(info.context.user).id
        resolved_value = Profile.objects.filter(
            business_id=business_id).order_by('-created_at')
            
        if offline:
            return resolved_value

        if page_count or page_number:
            customers = pagination_query(
                resolved_value, page_count, page_number)
            Query.pagination_result = customers
            return customers[0]
        paginated_response = pagination_query(resolved_value,
                                              PAGINATION_DEFAULT["page_count"],
                                              PAGINATION_DEFAULT["page_number"]
                                              )
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_total_customers_count(self, info, **kwargs):
        business_id = get_user_business(info.context.user).id
        customers_list = Profile.objects.filter(
            business_id=business_id)
        return len(customers_list)

    @login_required
    def resolve_total_customers_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying totalCustomersPagesCount query field should
        strictly be called after the customers query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_customer(self, info, **kwargs):
        search = kwargs.get('search')
        name = kwargs.get('name')
        mobile_number = kwargs.get('mobile_number')
        customer_id = kwargs.get('customer_id')

        if search:
            resolved_value = Profile.objects.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(primary_mobile_number=search) |
                Q(secondary_mobile_number=search))
            if not resolved_value:
                name_query_error =\
                    CUSTOMER_ERROR_RESPONSES[
                        "customer_profile_not_found"].format(name)
                raise GraphQLError(name_query_error)
            return resolved_value

        if name:
            resolved_value = Profile.objects.filter(
                Q(first_name__iexact=name) | Q(
                    last_name__iexact=name))
            if not resolved_value:
                name_query_error =\
                    CUSTOMER_ERROR_RESPONSES[
                        "customer_name_query_error"].format(name)
                raise GraphQLError(name_query_error)
            return resolved_value

        if mobile_number:
            resolved_value = Profile.objects.filter(
                Q(primary_mobile_number=mobile_number) |
                Q(secondary_mobile_number=mobile_number))
            if not resolved_value:
                mobile_query_error =\
                    CUSTOMER_ERROR_RESPONSES[
                        "customer_mobile_query_error"].format(name)
                raise GraphQLError(mobile_query_error)
            return resolved_value

        if customer_id:
            resolved_value = get_model_object(Profile, 'id', customer_id)
            return (resolved_value,)

        return None

    @login_required
    def resolve_filter_customers(self, info, **kwargs):
        for key in kwargs:
            if key == 'email__iexact':
                EmailValidator(
                    message=CUSTOMER_ERROR_RESPONSES["invalid_email"])(
                    kwargs[key])
            else:
                RegexValidator(
                    r"^[0-9a-zA-Z\']+$",
                    "Please provide a valid search keyword."
                    " Only letters, numbers, and apostrophes allowed")(
                    kwargs[key])


        page_count=kwargs.get('page_count')
        page_number=kwargs.get('page_number')

        kwargs.pop('page_count', None)
        kwargs.pop('page_number', None)

        resolved_value = Profile.objects.filter(
            **kwargs).order_by('first_name')    
        
        if not resolved_value:
            queries = ', '.join(list(kwargs.values()))
            query_error =\
                CUSTOMER_ERROR_RESPONSES[
                    "customer_query_error"].format(queries)
            raise GraphQLError(query_error)
        
        if page_count or page_number:
            customers = pagination_query(
                resolved_value, page_count, page_number)
            Query.pagination_result = customers
            return customers[0]
            
        paginated_response = pagination_query(resolved_value,
                                              PAGINATION_DEFAULT["page_count"],
                                              PAGINATION_DEFAULT["page_number"]
                                              )
        Query.pagination_result = paginated_response
        return paginated_response[0]  

