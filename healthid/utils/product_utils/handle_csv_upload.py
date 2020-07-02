import csv
from re import sub
import datetime
from django.utils.dateparse import parse_date
from rest_framework.exceptions import NotFound, ValidationError
from healthid.apps.products.models import Product

from healthid.apps.business.models import Business
from healthid.apps.orders.models.suppliers import SuppliersMeta
from healthid.apps.products.models import (BatchInfo, Product, DispensingSize, Product,
                                           ProductCategory, Quantity)
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.product_utils.product import \
    generate_reorder_points_and_max
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES
from healthid.utils.product_utils.batch_utils import batch_info_instance
from healthid.utils.product_utils.validate_products_csv_upload import\
    validate_products_csv_upload
from healthid.utils.product_utils.check_product_category import\
    check_product_category
from healthid.utils.get_on_duplication_csv_upload_actions import\
    get_on_duplication_csv_upload_actions
from healthid.utils.product_utils.check_product import\
    check_product
from healthid.utils.product_utils.metadata_handler import add_product_metadata, update_product_metadata
from healthid.utils.product_utils.csv_upload_helper import \
    map_quickbooks_data_helper, map_retail_pro_data_helper, create_batch_helper, create_out_of_stock_batch
from healthid.apps.orders.models.suppliers import Suppliers


class HandleCsvValidations(object):
    def handle_csv_upload(self, io_string, user, on_duplication):
        """
        Parses products information from an appropriately formatted CSV file
        and save them.
        arguments:
            io_string(obj): 'io.StringIO' object containing a list
                            of products in CSV format
        returns:
            int: the number of saved products
        """
        on_duplication_actions = get_on_duplication_csv_upload_actions(
            on_duplication)
        params = {'model': Product, 'error_type': ValidationError}
        [product_count, row_count, duplicated_products] = [0, 0, []]
        products = validate_products_csv_upload(io_string)
        user_bussinesses = Business.objects.filter(user_id=user.id).values()
        for row in products:
            row_count += 1
            category = row.get('category') or row.get('product category')
            product_categories = ProductCategory.objects.filter(
                name__iexact=category).values()

            product_name = row.get('name') or row.get('product name')
            on_duplicate_action = on_duplication_actions.get(
                product_name.lower()) or ''
            product_category = check_product_category(
                user_bussinesses, product_categories, category, row_count)

            supplier = get_model_object(SuppliersMeta,
                                        'display_name__iexact',
                                        row.get('preferred supplier'),
                                        error_type=NotFound,
                                        label='Display name')

            backup_supplier = get_model_object(SuppliersMeta,
                                               'display_name__iexact',
                                               row.get('backup supplier'),
                                               error_type=NotFound,
                                               label='Display name')

            dispensing_size = get_model_object(DispensingSize,
                                               'name__iexact',
                                               row.get('dispensing size') or
                                               row.get('measurement unit'),
                                               error_type=NotFound,
                                               label='Dispensing size')

            vat_status = row.get('vat status').lower() == 'vat' or False\
                if row.get('vat status')\
                else product_category.get('is_vat_applicable')

            loyalty_weight = row.get('loyalty weight')\
                if str(row.get('loyalty weight')).isdigit()\
                else product_category.get('loyalty_weight')

            image = row.get('image') or row.get('product image')
            global_upc = row.get('global upc')
            
            current_products = Product.objects.filter(
                product_name__iexact=product_name).values()
            product = check_product(user_bussinesses,
                                    current_products,
                                    product_name,
                                    row_count,
                                    True)

            if not product:
                product_instance = Product(
                    product_category_id=product_category.get('id'),
                    business_id=product_category.get('business_id'),
                    product_name=product_name,
                    dispensing_size_id=dispensing_size.id,
                    description=row.get('description') or '',
                    brand=row.get('brand') or '',
                    manufacturer=row.get('manufacturer') or '',
                    vat_status=vat_status,
                    preferred_supplier_id=supplier.supplier_id,
                    backup_supplier_id=backup_supplier.supplier_id,
                    tags=row.get('tags') or '',
                    image=image or '',
                    loyalty_weight=loyalty_weight)

                product_count += 1
                product_instance.global_upc = global_upc
                generate_reorder_points_and_max(user.id, product_instance)
            elif on_duplicate_action.lower() != 'skip':
                duplicated_products.append({
                    'row': row_count,
                    'message': ERROR_RESPONSES['duplication_error'].format(
                        product_name),
                    'data': row,
                    'conflicts': Product.objects.filter(
                        product_name__iexact=product_name).values(
                        'id', 'product_name', 'sku_number')
                })
        return {
            'product_count': product_count,
            'duplicated_products': duplicated_products
        }

    def handle_batch_csv_upload(self, user, batch_info_csv):
        """
        Parses batch information from an appropriately formatted CSV file.
        Creates and saves new 'BatchInfo' instances.
        Updates the product quantities based on the new batches.
        arguments:
            user(obj): contains a 'User' instance
            batch_info_csv(obj): 'io.StringIO' object representing
                                 the batch info CSV
        returns:
            None
        """

        batch_record_format = [
            'Batch No',
            'Product',
            'Supplier',
            'Date Received',
            'Expiry Date',
            'Unit Cost',
            'Quantity Received',
            'Service Quality',
            'Delivery Promptness'
        ]
        true_strings = ['TRUE', 'True', 'true', 't']
        false_strings = ['FALSE', 'False', 'false', 'f']

        # produces the column header row of the CSV
        # from the iterator returned by csv.reader()
        row_count = 0
        column_header = next(csv.reader(batch_info_csv))
        user_bussinesses = Business.objects.filter(user_id=user.id).values()

        if column_header == batch_record_format:
            for batch_record in csv.reader(batch_info_csv):
                row_count += 1
                products = Product.objects.filter(
                    product_name__iexact=batch_record[1]).values()
                product = check_product(
                    user_bussinesses, products, batch_record[1], row_count)

                supplier_id = get_model_object(
                    SuppliersMeta,
                    'display_name',
                    batch_record[2],
                    error_type=NotFound
                ).supplier_id

                # check if batch expiry date occurs before delivery date.
                # 'batch_record[3]' and 'batch_record[2]' represent the
                # 'Expiry Date' and 'Delivery Date' CSV records respectively.
                if batch_record[4] < batch_record[3]:
                    raise ValidationError(
                        PRODUCTS_ERROR_RESPONSES["batch_expiry_error"].format
                        (batch_record[1])
                    )

                # converts a 'True' or 'False' string from the
                # 'Delivery Promptness' CSV column into a Python boolean.
                # 'batch_record[7]' represents the 'Delivery Promptness'
                #  CSV record.
                if batch_record[8] in true_strings:
                    batch_record[8] = True
                elif batch_record[8] in false_strings:
                    batch_record[8] = False
                else:
                    raise ValidationError(
                        PRODUCTS_ERROR_RESPONSES["batch_bool_error"]
                    )

                batch_info_args = {
                    'batch_no': batch_record[0],
                    'product_id': product.get('id'),
                    'supplier_id': supplier_id,
                    'date_received': batch_record[3],
                    'expiry_date': batch_record[4],
                    'unit_cost': float(batch_record[5]),
                    'quantity': int(batch_record[6]),
                    'service_quality': int(batch_record[7]),
                    'delivery_promptness': batch_record[8]
                }
                self.create_batch_info(user, **batch_info_args)
        else:
            raise ValidationError(PRODUCTS_ERROR_RESPONSES["batch_csv_error"])

    @batch_info_instance
    def create_batch_info(self, user, **kwargs):
        quantity = kwargs.pop('quantity')
        kwargs['date_received'] = parse_date(kwargs.get('date_received'))
        kwargs['expiry_date'] = parse_date(kwargs.get('expiry_date'))
        batch_info = BatchInfo(user=user)
        datetime_str = sub('[-]', '', str(kwargs['date_received']))
        batch_no_auto = f'BN{datetime_str}'
        if not kwargs.get('batch_no'):
            kwargs['batch_no'] = batch_no_auto
        batch_ = BatchInfo.objects.filter(batch_no=kwargs.get('batch_no'))
        batch__l = list(
            map(lambda batch__: batch__.quantity == quantity, batch_))
        if True in batch__l:
            raise ValidationError(
                ERROR_RESPONSES['batch_exist'].format(kwargs.get('batch_no')))
        for key, value in kwargs.items():
            setattr(batch_info, key, value)

        with SaveContextManager(batch_info, model=BatchInfo) as batch_info:
            quantity = Quantity(
                batch=batch_info, quantity_received=quantity,
                quantity_remaining=quantity, is_approved=True)
            quantity.save()
            generate_reorder_points_and_max(user.id, batch_info.product)

    def unapprove_stale_product(self, user, io_string):
        """
        Takes in a csv file and and marks all the products as approved
        arguments:
            io_string(obj): 'io.StringIO' object containing a list
                            of products in CSV format
        returns:
            int: the number of stale products.
        """
        stale_product_ids =[]
        line_count = 0
        for row in csv.DictReader(io_string):
            if line_count != 0:
                stale_product_ids.append(row['product_id'])
            line_count += 1

        Product.objects.filter(id__in = stale_product_ids).update(is_approved = False)
        return len(stale_product_ids)

    def handle_retail_pro_csv_upload(self, io_string, user):
        """
        Maps products information from a retail pro csv file to a Health ID
        formatted CSV file
        and save them.
        arguments:
            io_string(obj): 'io.StringIO' object containing a list
                            of products in CSV format
        returns:
            int: the number of saved products
        """
        product_count = error_count = update_count = 0
        business = Business.objects.filter(user_id=user.id).first()
        default_retail_pro_supplier = Suppliers.objects.filter(
            supplier_id="retail").first()
        if not business:
            return {'product_count': product_count, 'business_id': None}
        for row in csv.DictReader(io_string):
            result = map_retail_pro_data_helper(
                row, business, user, default_retail_pro_supplier)
            if result['action'] == "create":
                try:
                    with SaveContextManager(result['product_instance'], model=Product) as product:
                        add_product_metadata(product, result['product_meta_args'])
                        if int(result['qty']) > 0:
                            create_batch_helper(
                                product, user, result['supplier_id'], result['unit_cost'], result['qty'], tag="MRP")
                            create_out_of_stock_batch(
                                product, user, result['supplier_id'], result['unit_cost']
                                )
                        product_count += 1
                        generate_reorder_points_and_max(user.id,product)
                
                except Product.MultipleObjectsReturned:
                    error_count+=1

            elif result['action'] == "update":
                try:
                    with SaveContextManager(result['product_instance'], model=Product) as product:
                        update_product_metadata(product, result['product_meta_args'])
                        if int(result['qty']) > 0:
                            create_batch_helper(
                                product, user, result['supplier_id'], result['unit_cost'], result['qty'], tag="MRP")
                        update_count += 1
                        generate_reorder_points_and_max(user.id,product)
                except Product.MultipleObjectsReturned:
                    error_count+=1

        return {
                'update_count':update_count,
                'error_count':error_count,
                'product_count': product_count,
                'business_id': business.id
            }

    def handle_quick_box_csv_upload(self, io_string, user):
        """
        Maps products information from a quick box csv file to a Health ID
        formatted CSV file
        and save them.
        arguments:
            io_string(obj): 'io.StringIO' object containing a list
                            of products in CSV format
        returns:
            int: the number of saved products
        """
        product_count = update_count = error_count = 0
        business = Business.objects.filter(user_id=user.id).first()
        default_quickbox_supplier = Suppliers.objects.filter(
            supplier_id="quickbook").first()
        if not business:
            return {'product_count': product_count, 'business_id': None}
        product_count = 0
        for row in csv.DictReader(io_string):
            result = map_quickbooks_data_helper(
                row, business, user, default_quickbox_supplier)

            if result['action'] == 'create':
                try:
                    with SaveContextManager(result['product_instance'], model=Product) as product:
                        add_product_metadata(product, result['product_meta_args'])
                        if int(result['qty']) > 0:
                            create_batch_helper(
                                product, user, result['supplier_id'], result['unit_cost'], result['qty'], tag="MQB"
                                )
                            create_out_of_stock_batch(
                                product, user, result['supplier_id'], result['unit_cost']
                                )
                        product_count += 1
                        generate_reorder_points_and_max(user.id, product)
                except Product.MultipleObjectsReturned:
                    error_count+=1

            elif result['action'] == 'update':
                try:
                    with SaveContextManager(result['product_instance'], model=Product) as product:
                        update_product_metadata(product, result['product_meta_args'])
                        if int(result['qty']) > 0:
                            create_batch_helper(
                                product, user, result['supplier_id'], result['unit_cost'], result['qty'], tag="MQB")
                        update_count += 1
                        generate_reorder_points_and_max(user.id,product)
                except Product.MultipleObjectsReturned:
                    error_count+=1
                
        return {
                'update_count':update_count, 
                'product_count': product_count,
                'error_count':error_count, 
                'business_id': business.id
                }
