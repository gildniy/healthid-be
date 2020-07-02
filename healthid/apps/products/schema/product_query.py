from datetime import datetime
from dateutil.relativedelta import relativedelta

import graphene
from django.core.exceptions import ValidationError
from graphene.utils.resolve_only_args import resolve_only_args
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from taggit.managers import TaggableManager

from healthid.apps.products.models import (BatchInfo, DispensingSize, Product,
                                           ProductCategory, ProductMeta, Quantity, Survey)
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT
from healthid.utils.app_utils.validators import validate_expire_months
from healthid.apps.orders.services import SaveAutofillItems
from healthid.apps.orders.models.orders import OrdersProducts, ProductBatch
from healthid.utils.app_utils.get_user_business import get_user_business


@convert_django_field.register(TaggableManager)
def convert_field_to_string(field, registry=None):
    return graphene.List(graphene.String, source='get_tags')


class BatchInfoType(DjangoObjectType):
    quantity = graphene.Int()
    proposed_quantity = graphene.Int()

    class Meta:
        model = BatchInfo

    def resolve_quantity(self, info, **kwargs):
        return self.quantity

    def resolver_proposed_quantity(self, info, **kwargs):
        return self.proposed_quantity


class ProductCategoryType(DjangoObjectType):
    class Meta:
        model = ProductCategory


class DispensingSizeType(DjangoObjectType):
    class Meta:
        model = DispensingSize


class ProductType(DjangoObjectType):
    quantity_in_stock = graphene.Int()
    product_quantity = graphene.Int()
    sales_price = graphene.Float()
    pre_tax_retail_price = graphene.Float()
    unit_cost = graphene.Int()
    pre_ordered_quantity = graphene.Int()
    global_upc = graphene.String()
    description = graphene.String()

    class Meta:
        model = Product
        filter_fields = {
            'is_approved': ['exact'],
            'product_name': ['exact', 'icontains', 'istartswith'],
            'sku_number': ['exact'],
            'tags__name': ['exact', 'icontains', 'istartswith'],
            'description': ['exact', 'icontains', 'istartswith']
        }
        interfaces = (graphene.relay.Node,)

    def resolve_pre_ordered_quantity(self, info):
        return self.pre_ordered_quantity()

    def resolve_quantity_in_stock(self, info, **kwargs):
        return self.quantity_in_stock

    def resolve_pre_tax_retail_price(self, info, **kwargs):
        return self.pre_tax_retail_price

    def resolve_unit_cost(self, info, **kwargs):
        return self.avarage_unit_cost

    def resolve_product_quantity(self, info, **kwargs):
        return self.product_quantity

    id = graphene.ID(required=True)

    @resolve_only_args
    def resolve_id(self):
        return self.id


class AutofillProductType(DjangoObjectType):
    class Meta:
        model = OrdersProducts


class QuantityType(DjangoObjectType):
    id = graphene.String()
    quantity_received = graphene.Int()

    class Meta:
        model = Quantity


class SurveyType(DjangoObjectType):
    class Meta:
        model = Survey


class Query(graphene.AbstractType):
    pagination_result = None

    products = graphene.List(ProductType,
                             search=graphene.String(),
                             page_count=graphene.Int(),
                             page_number=graphene.Int()
                             )
    proposed_products = graphene.List(ProductType, page_count=graphene.Int(),
                                      page_number=graphene.Int())
    all_batch_info = graphene.List(BatchInfoType)
    batch_info = graphene.Field(
        BatchInfoType, id=graphene.String(required=True))
    product_batch_info = graphene.List(
        BatchInfoType, id=graphene.Int(required=True))
    approved_products = graphene.List(ProductType, page_count=graphene.Int(),
                                      page_number=graphene.Int())
    filter_products = DjangoFilterConnectionField(
        ProductType,
        page_count=graphene.Int(),
        page_number=graphene.Int()
    )
    proposed_edits = graphene.List(
        ProductType, page_count=graphene.Int(), page_number=graphene.Int())
    proposed_edit = graphene.Field(ProductType, id=graphene.Int(required=True))
    price_check_surveys = graphene.List(SurveyType)
    price_check_survey = graphene.Field(
        SurveyType, id=graphene.String(required=True))
    user_product_requests = graphene.List(ProductType)
    approved_quantities = graphene.List(QuantityType)
    declined_quantities = graphene.List(QuantityType)

    products_order = graphene.List(
        AutofillProductType, order_id=graphene.Int(required=True))
    product = graphene.Field(
        ProductType,
        id=graphene.Int(),
        product_name=graphene.String(),
        sku_number=graphene.Int(),
        description=graphene.String(),
        brand=graphene.String(),
        manufacturer=graphene.String(),
        sales_price=graphene.Int(),
        nearest_expiry_date=graphene.String(),
        tags=graphene.List(graphene.String))
    near_expired_products = graphene.List(ProductType,
                                          page_count=graphene.Int(),
                                          page_number=graphene.Int())
    batch_expiries = graphene.Field(
        product_batch_info,
        start_date=graphene.String(),
        end_date=graphene.String(required=True))
    expired_batches = graphene.Field(product_batch_info)
    deactivated_products = graphene.List(ProductType)
    product_categories = graphene.List(
        ProductCategoryType, business_id=graphene.String(required=False))
    dispensing_size = graphene.List(DispensingSizeType)
    total_products_pages_count = graphene.Int()
    products_total_number = graphene.Int()
    near_expired_products = graphene.List(ProductType,
                                          page_count=graphene.Int(),
                                          page_number=graphene.Int(),
                                          expire_month=graphene.Int())
    near_expired_batches = graphene.List(BatchInfoType,
                                         page_count=graphene.Int(),
                                         page_number=graphene.Int(),
                                         expire_month=graphene.Int())

    @login_required
    def resolve_supplier_autofill(self, info):
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)
        product_list = []

        for product in Product.objects.for_business(business.id):
            pre_ordered_product_quantity = Product.pre_ordered_quantity(
                product)

            if (product.quantity_in_stock +
                    pre_ordered_product_quantity) < product.reorder_point:
                product_list.append(product)
        return product_list

    @login_required
    def resolve_products(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        search = (kwargs.get('search') or '').strip()
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)
        products_set = Product.all_products.for_business(
            business.id).filter(parent_id__isnull=True).order_by('id')

        if search:
            search_filter = Product.general_search(search)
            products_set = products_set.filter(search_filter)

        if page_count or page_number:
            products = pagination_query(
                products_set, page_count, page_number)
            Query.pagination_result = products
            return products[0]
        Query.attach_upc_to_products(products_set)
        paginated_response = pagination_query(products_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response

        return paginated_response[0]

    @login_required
    def resolve_total_products_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying, totaLProductsPagesCount query field should
        strictly be called after the products query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_products_total_number(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of items for a specific pagination response
        :Note: During querying, productsTotalNumber query field should
        strictly be called after the products query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]

    @login_required
    def resolve_filter_products(self, info, **kwargs):
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)

        page_count=kwargs.get('page_count')
        page_number=kwargs.get('page_number')

        kwargs.pop('page_count', None)
        kwargs.pop('page_number', None)

        for key in kwargs:
            if isinstance(kwargs[key], str) and kwargs[key].strip() == "":
                raise GraphQLError(
                    PRODUCTS_ERROR_RESPONSES["invalid_search_key"])

        approved_products = \
            Product.all_products.for_business(business.id).filter(
                parent_id__isnull=True)
        products = list(approved_products.filter(
            **kwargs).order_by("product_name"))
        global_upc_products = Query.get_products_according_to_upc(
            approved_products, kwargs)
        matched_description = Query.get_products_by_description(
            approved_products, 
            kwargs
        )

        products += matched_description
        # Attach the UPC when a user search with the product name but not a UPC
        Query.attach_upc_to_products(products)

        response = list(set(global_upc_products + products))

        if not response:
            raise GraphQLError(
                PRODUCTS_ERROR_RESPONSES["inexistent_product_query"])

        if page_count or page_number:
            filtered_products = pagination_query(
                response, page_count, page_number)
            Query.pagination_result = filtered_products
            return filtered_products[0]
            
        paginated_response = pagination_query(response,
                                              PAGINATION_DEFAULT["page_count"],
                                              PAGINATION_DEFAULT["page_number"]
                                              )
        Query.pagination_result = paginated_response
        return paginated_response[0]

    def get_data_value(kwargs):
        data_value = ''
        for arg in kwargs:
            data_value = kwargs[arg] if "product_name" in arg else ''
        return data_value

    def attach_upc_to_products(approved_products):
        product_meta = []
        for product in approved_products:
            product_meta.append(list(ProductMeta.objects.filter(
                dataKey='global_upc', product_id=product.id)))

        # flatten the list i.e convert from 2D to 1D
        product_meta = [item for sublist in product_meta for item in sublist]

        for p_meta in product_meta:
            for product in approved_products:
                if product.id == p_meta.product_id:
                    product.global_upc = p_meta.dataValue

    @staticmethod
    def get_products_according_to_upc(approved_products, kwargs):
        product_ids = []
        product_dict = {}
        for product in approved_products:
            product_ids.append(product.id)
            product_dict[product.id] = product

        data_value = Query.get_data_value(kwargs)
        product_meta = list(ProductMeta.objects.filter(
            dataKey='global_upc',
            dataValue__icontains=data_value,
            product_id__in=product_ids,
        ))

        result = []
        for p_meta in product_meta:
            product_dict[p_meta.product_id].global_upc = p_meta.dataValue
            result.append(product_dict[p_meta.product_id])

        return result

    @staticmethod
    def get_products_by_description(approved_products, kwargs):
        product_ids = []
        product_dict = {}
        for product in approved_products:
            product_ids.append(product.id)
            product_dict[product.id] = product

        search_term = Query.get_data_value(kwargs)
        matches = Product.objects.filter(
            pk__in=product_ids,
            description__contains=search_term
        )

        return list(matches)

    @login_required
    def resolve_proposed_products(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)
        proposed_products_set = Product.all_products.for_business(
            business.id).filter(
            is_approved=False, parent_id__isnull=True).order_by('id')
        Query.attach_upc_to_products(proposed_products_set)

        if page_count or page_number:
            proposed_products = pagination_query(
                proposed_products_set, page_count, page_number)
            Query.pagination_result = proposed_products
            return proposed_products[0]
        paginated_response = pagination_query(proposed_products_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_approved_products(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)
        approved_products_set = Product.objects.for_business(
            business.id).filter(is_approved=True).order_by('id')
        Query.attach_upc_to_products(approved_products_set)

        if page_count or page_number:
            approved_products = pagination_query(
                approved_products_set, page_count, page_number)
            Query.pagination_result = approved_products
            return approved_products[0]
        paginated_response = pagination_query(approved_products_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_near_expired_products(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        expire_month = validate_expire_months(kwargs.get('expire_month'))
        today_date = datetime.now()
        expire_range = today_date + relativedelta(months=+expire_month)
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)
        near_expired_products_set = Product.objects \
            .for_business(business.id) \
            .filter(nearest_expiry_date__range=(today_date, expire_range)) \
            .order_by('id')
        if page_count or page_number:
            approved_products = pagination_query(
                near_expired_products_set, page_count, page_number)
            Query.pagination_result = approved_products
            return approved_products[0]
        paginated_response = pagination_query(near_expired_products_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_product(self, info, **kwargs):
        id = kwargs.get('id')
        if id:
            product = []
            product.append(get_model_object(Product, 'id', id))
            Query.attach_upc_to_products(product)
            return product[0]
        raise GraphQLError(ERROR_RESPONSES["invalid_field_error"].format(id))

    @login_required
    def resolve_proposed_edits(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)
        proposed_edits_set = Product.all_products.for_business(
            business.id).exclude(
            parent_id__isnull=True)
        Query.attach_upc_to_products(proposed_edits_set)

        if page_count or page_number:
            proposed_edits = pagination_query(
                proposed_edits_set, page_count, page_number)
            Query.pagination_result = proposed_edits
            return proposed_edits[0]
        paginated_response = pagination_query(proposed_edits_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_proposed_edit(self, info, **kwargs):
        proposed_edit_id = kwargs.get('id')
        if proposed_edit_id:
            user = info.context.user
            check_user_has_an_active_outlet(user)
            business = get_user_business(user)
            proposed_edit = Product.all_products.for_business(
                business.id).filter(id=proposed_edit_id).exclude(
                parent_id__isnull=True).first()
            if not proposed_edit:
                raise GraphQLError(
                    ERROR_RESPONSES["proposed_edit_inexistant"].format(
                        proposed_edit_id))
            return proposed_edit
        raise GraphQLError(ERROR_RESPONSES["invalid_field_error"].format('id'))

    @login_required
    def resolve_product_categories(self, info, **kwargs):
        business_id = kwargs.get('business_id')
        return ProductCategory.objects.filter(business_id=business_id)

    @login_required
    def resolve_dispensing_size(self, info):
        return DispensingSize.objects.all()

    @login_required
    def resolve_price_check_surveys(self, info):
        return Survey.objects.all()

    @login_required
    def resolve_price_check_survey(self, info, **kwargs):
        return get_model_object(Survey, 'id', kwargs.get('id'))

    @login_required
    def resolve_user_product_requests(self, info, **kwargs):
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)
        return Product.all_products.for_business(business.id).filter(
            user=user).exclude(parent=None)

    @login_required
    def resolve_products_order(self, info, **kwargs):
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)
        order_id = kwargs.get("order_id")
        product_list = []

        for product in Product.objects.filter(business_id=business.id, is_approved=True):
            pre_ordered_product_quantity = Product.pre_ordered_quantity(
                product)

            if (product.quantity_in_stock +
                    pre_ordered_product_quantity) < product.reorder_point:
                product_list.append(product)
        if len(product_list) == 0:
            return product_list

        saved_products = SaveAutofillItems(
            product_list, order_id).save()
        return saved_products


class BatchQuery(graphene.AbstractType):
    all_batch_info = graphene.List(BatchInfoType)
    batch_info = graphene.Field(
        BatchInfoType, id=graphene.String(required=True))
    batch_quantity = graphene.Field(
        QuantityType, id=graphene.String(required=True))
    product_batch_info = graphene.List(
        BatchInfoType, id=graphene.Int(required=True))
    proposed_quantity_edits = graphene.List(QuantityType)
    total_batches_pages_count = graphene.Int()
    batches_total_number = graphene.Int()
    near_expired_batches = graphene.List(BatchInfoType,
                                         page_count=graphene.Int(),
                                         page_number=graphene.Int(),
                                         expire_month=graphene.Int())

    @login_required
    def resolve_all_batch_info(self, info):
        return BatchInfo.objects.all()

    @login_required
    def resolve_batch_info(self, info, **kwargs):
        id = kwargs.get('id')
        batch = get_model_object(BatchInfo, 'id', id)
        return batch

    @login_required
    def resolve_product_batch_info(self, info, **kwargs):
        product = get_model_object(Product, 'id', kwargs.get('id'))
        product_batches = product.batch_info.all()
        return product_batches

    @login_required
    def resolve_batch_expiries(self, info, **kwargs):

        start_date = kwargs.get("start_date") or datetime.now()
        end_date = kwargs.get("end_date")
        try:
            return BatchInfo.objects.filter(
                expiry_date__range=(start_date, end_date))
        except ValidationError as e:
            raise GraphQLError("The {}".format(e.messages[0]))

    @login_required
    def resolve_expired_batches(self, info, **kwargs):
        start_date = datetime.now()
        return BatchInfo.objects.filter(expiry_date__lt=start_date)

    @login_required
    @user_permission('Operations Admin')
    def resolve_deactivated_products(self, info, **kwargs):
        user = info.context.user
        check_user_has_an_active_outlet(user)
        business = get_user_business(user)
        return Product.all_products.for_business(business.id).filter(
            is_active=False)

    @login_required
    @user_permission('Manager', 'Operations Admin')
    def resolve_proposed_quantity_edits(self, info):
        return Quantity().get_proposed_quantities()

    @login_required
    @user_permission('Operations Admin')
    def resolve_approved_quantities(self, info):
        return Quantity.objects.filter(
            parent_id__isnull=True, is_approved=True)

    @login_required
    @user_permission('Operations Admin')
    def resolve_declined_quantities(self, info):
        return Quantity.objects.filter(
            parent_id__isnull=True, request_declined=True)

    @login_required
    def resolve_near_expired_batches(self, info, **kwargs):
        page_count = kwargs.get('page_count') or \
            PAGINATION_DEFAULT["page_count"]
        page_number = kwargs.get(
            'page_number') or PAGINATION_DEFAULT["page_number"]
        expire_month = validate_expire_months(kwargs.get('expire_month'))
        today_date = datetime.now()
        expire_range = today_date + relativedelta(months=+expire_month)
        near_expired_batches_set = BatchInfo.objects \
            .filter(expiry_date__range=(today_date, expire_range)) \
            .order_by('expiry_date')

        near_expired_batches = pagination_query(near_expired_batches_set,
                                                page_count,
                                                page_number)
        Query.pagination_result = near_expired_batches
        return near_expired_batches[0]

    @login_required
    def resolve_total_batches_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying, totaLProductsPagesCount query field should
        strictly be called after the products query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_batches_total_number(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of items for a specific pagination response
        :Note: During querying, productsTotalNumber query field should
        strictly be called after the products query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[2]
