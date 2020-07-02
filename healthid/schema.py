import graphene
import graphql_jwt

from healthid.apps.authentication.schema import (AuthMutation, AuthQuery,
                                                 ObtainJSONWebToken)
from healthid.apps.business.schema import business_mutation, business_query
from healthid.apps.consultation.schema.mutations import \
    consultation_catalogue_mutation
from healthid.apps.consultation.schema.\
    queries import (consultation_query, schedule_consultation_query)
from healthid.apps.notifications.schema import (notification_mutations,
                                                notification_queries)
from healthid.apps.orders.schema import (SuppliersMutation, SuppliersQuery,
                                         order_mutations, order_query,
                                         barcode_mutations)
from healthid.apps.outlets.schema import outlet_mutation, outlet_schema
from healthid.apps.preference.schema import (preference_mutation,
                                             preference_schema)
from healthid.apps.products.schema import product_mutations, product_query
from healthid.apps.receipts.schema import receipt_mutation, receipt_schema
from healthid.apps.register.schema import register_mutation, register_schema
from healthid.apps.sales.schema import (sales_mutation, sales_schema,
                                        promotions_mutation, promotions_query,
                                        cart_mutation, cart_query, sales_query,
                                        near_expire_promotion)
from healthid.apps.events.schema import event_querys, event_mutations
from healthid.apps.stock.schema.mutations import stock_mutation
from healthid.apps.stock.schema.queries import stock_query
from healthid.apps.customers.schema import customer_mutation, customer_query
from healthid.apps.orders.schema import invoices_mutation
from healthid.apps.wallet.schema import wallet_mutation, wallet_query
from healthid.apps.despatch_queue.schema import despatch_mutation


class Query(
        AuthQuery,
        business_query.Query,
        outlet_schema.Query,
        preference_schema.Query,
        SuppliersQuery,
        receipt_schema.Query,
        register_schema.Query,
        product_query.Query,
        product_query.BatchQuery,
        event_querys.Query,
        consultation_query.Query,
        schedule_consultation_query.Query,
        sales_schema.Query,
        sales_query.Query,
        promotions_query.Query,
        stock_query.Query,
        notification_queries.Query,
        cart_query.Query,
        customer_query.Query,
        order_query.Query,
        wallet_query.CustomerCreditQuery,
        graphene.ObjectType):
    pass


class Mutation(
        AuthMutation,
        business_mutation.Mutation,
        outlet_mutation.Mutation,
        preference_mutation.Mutation,
        SuppliersMutation,
        receipt_mutation.Mutation,
        register_mutation.Mutation,
        product_mutations.Mutation,
        event_mutations.Mutation,
        notification_mutations.Mutation,
        sales_mutation.Mutation,
        consultation_catalogue_mutation.Mutation,
        promotions_mutation.Mutation,
        stock_mutation.Mutation,
        order_mutations.Mutation,
        barcode_mutations.Mutation,
        customer_mutation.Mutation,
        cart_mutation.Mutation,
        invoices_mutation.Mutation,
        wallet_mutation.Mutation,
        near_expire_promotion.Mutation,
        despatch_mutation.Mutation,
        graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(mutation=Mutation, query=Query)
