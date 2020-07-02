import csv
import io
import traceback
import sys
from django.shortcuts import render
from django.db.models import Count, Sum, F
from django.http import HttpResponse
from rest_framework import status
from rest_framework.authentication import (SessionAuthentication,
                                           TokenAuthentication)
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from healthid.apps.products.models import Product, BatchInfo
from healthid.apps.orders.models.suppliers import \
    (Suppliers, SuppliersContacts, SuppliersMeta)
from healthid.apps.profiles.models import Profile
from healthid.apps.products.serializers import ProductsSerializer
from healthid.utils.orders_utils.add_supplier import AddSupplier
from healthid.utils.product_utils.handle_csv_export import handle_csv_export
from healthid.utils.product_utils.handle_csv_upload import HandleCsvValidations
from healthid.utils.constants.product_constants import (
    PRODUCT_INCLUDE_CSV_FIELDS, BATCH_INFO_CSV_FIELDS)
from healthid.utils.constants.customer_constants import (
    CUSTOMERS_INCLUDE_CSV_FIELDS)
from healthid.utils.constants.suppliers_infor_constants import \
    SUPPLIERS_INCLUDE_CSV_FIELDS
from healthid.utils.csv_export.generate_csv import generate_csv_response
from healthid.utils.customer_utils.handle_customer_csv_upload import\
    HandleCustomerCSVValidation
from healthid.utils.messages.common_responses import ERROR_RESPONSES
from healthid.utils.messages.products_responses import (
    PRODUCTS_SUCCESS_RESPONSES
)


class HandleCSV(APIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    parser_classes = (MultiPartParser, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, param, format=None):
        """
        Rest API post method that is meant to handle the mass,
        upload of information from csv files
        :param request: Will be used to extract the file type
        :param param: endpoint parameter confirming the nature of info,
                      expected in the csv
        :param format:
        :return: Throws error on validation failure and returns,
                  success on Successful data upload
        """
        handle_csv_object = HandleCsvValidations()
        handle_customer_csv_object = HandleCustomerCSVValidation()
        handle_supplier_csv_object = AddSupplier()
        retail_pro_suppliers = handle_supplier_csv_object.retail_pro_suppliers
        quick_books_suppliers = \
            handle_supplier_csv_object.quick_books_suppliers
        handle_csv = handle_csv_object.handle_csv_upload
        retail_pro_csv_upload = handle_csv_object.handle_retail_pro_csv_upload
        quick_box_csv_upload = handle_csv_object.handle_quick_box_csv_upload
        handle_supplier_csv = handle_supplier_csv_object.handle_csv_upload
        handle_customer_csv_upload =\
            handle_customer_csv_object.handle_customer_csv_upload
        handle_cutomer_retail_pro_csv_upload =\
            handle_customer_csv_object.handle_cutomer_retail_pro_csv_upload
        handle_cutomer_quickbooks_csv_upload =\
            handle_customer_csv_object.handle_cutomer_quickbooks_csv_upload
        csv_file = request.FILES['file']

        if not csv_file.name.endswith('.csv'):
            message = {"error": "Please upload a csv file"}
            return Response(message, status.HTTP_400_BAD_REQUEST)
        data_set = csv_file.read().decode('UTF-8')

        io_string = io.StringIO(data_set)
        on_duplication = request.POST.get('on_duplication')
        try:
            if param == 'suppliers':
                user = request.user
                res = handle_supplier_csv(user=user,
                                          io_string=io_string,
                                          on_duplication=on_duplication)
                added_suppliers = res['supplier_count']
                message = {
                    "success": "Successfully added supplier(s)",
                    "noOfSuppliersAdded": res['supplier_count'],
                    "duplicatedSuppliers": res['duplicated_suppliers'],
                }
                if added_suppliers == 0 and len(res['duplicated_suppliers']):
                    return Response(
                        {
                            "message":
                            "No supplier has been added due to duplication",
                            "duplicatedSuppliers": res['duplicated_suppliers']
                        },
                        status.HTTP_400_BAD_REQUEST
                    )
                return Response(message, status.HTTP_201_CREATED)

            if param == 'retail_pro_suppliers':
                user = request.user
                res = retail_pro_suppliers(user=user,
                                           io_string=io_string,
                                           on_duplication=on_duplication)
                added_suppliers = res['supplier_count']
                message = {
                    "success": "Successfully added supplier(s)",
                    "noOfSuppliersAdded": res['supplier_count'],
                    "duplicatedSuppliers": res['duplicated_suppliers'],
                }
                if added_suppliers == 0 and len(res['duplicated_suppliers']):
                    return Response(
                        {
                            "message":
                            "No supplier has been added due to duplication",
                            "duplicatedSuppliers": res['duplicated_suppliers']
                        },
                        status.HTTP_400_BAD_REQUEST
                    )
                return Response(message, status.HTTP_201_CREATED)
            if param == 'quick_books_suppliers':
                user = request.user
                res = quick_books_suppliers(user=user,
                                            io_string=io_string,
                                            on_duplication=on_duplication)
                added_suppliers = res['supplier_count']
                message = {
                    "success": "Successfully added supplier(s)",
                    "noOfSuppliersAdded": res['supplier_count'],
                    "duplicatedSuppliers": res['duplicated_suppliers'],
                }
                if added_suppliers == 0 and len(res['duplicated_suppliers']):
                    return Response(
                        {
                            "message":
                            "No supplier has been added due to duplication",
                            "duplicatedSuppliers": res['duplicated_suppliers']
                        },
                        status.HTTP_400_BAD_REQUEST
                    )
                return Response(message, status.HTTP_201_CREATED)

            if param == 'products':
                user = request.user
                result = handle_csv(io_string=io_string,
                                    user=user,
                                    on_duplication=on_duplication)
                message = {
                    "message": ("Products successfully added"
                                if result['product_count']
                                else "No new products added"),
                    "noOfProductsAdded": result['product_count'],
                    "duplicatedProducts": result['duplicated_products'],
                }
                return Response(message,
                                status.HTTP_201_CREATED
                                if result['product_count']
                                else status.HTTP_400_BAD_REQUEST)
            if param == 'retail_pro_products':
                user = request.user
                result = retail_pro_csv_upload(io_string=io_string,
                                               user=user)
                if result['business_id']:
                    message = {"message": ("Products successfully added"
                                           if result['product_count']
                                           else "No new products added"),
                               "noOfProductsAdded": result['product_count'],
                               "noOfProductsUpdated": result['update_count'],
                               "noOfErrorsEncountered": result['error_count']
                               }
                    return Response(message,
                                    status.HTTP_201_CREATED
                                    if result['product_count']  or result['update_count']
                                    else status.HTTP_400_BAD_REQUEST
                                    )
                else:
                    message = \
                        {"message":
                         "Business id associated with this user is not found"
                         }
                    return Response(message)
            if param == 'quick_books_products':
                user = request.user
                result = quick_box_csv_upload(io_string=io_string,
                                              user=user)
                if result['business_id']:
                    message = {"message": ("Products successfully added"
                                           if result['product_count']
                                           else "No new products added"),
                               "noOfProductsAdded": result['product_count'],
                               "noOfProductsUpdated": result['update_count'],
                               "noOfErrorsEncountered": result['error_count']
                               }
                    return Response(message,
                                    status.HTTP_201_CREATED
                                    if (result['product_count'] or result['update_count'])
                                    else status.HTTP_400_BAD_REQUEST
                                    )
                else:
                    message = {"message": "Business id associated with this user is not found"
                               }
                    return Response(message)
            if param == 'customers':
                user = request.user
                result = handle_customer_csv_upload(
                    io_string=io_string, user=user)
                message = {
                    "message": ("Customers successfully added"
                                if result
                                else "No new customers added"),
                    "noOfCustomersAdded": result
                }
                return Response(message,
                                status.HTTP_201_CREATED
                                if result
                                else status.HTTP_400_BAD_REQUEST
                                )

            if param == 'retail_pro_customers':
                user = request.user
                result, duplicate_counts = handle_cutomer_retail_pro_csv_upload(
                    io_string=io_string, user=user)
                message = {
                    "message": ("Customers successfully added"
                                if result
                                else "No new customers added"),
                    "noOfCustomersAdded": result,
                    "noOfDuplicates": duplicate_counts
                }
                return Response(message,
                                status.HTTP_201_CREATED
                                if result
                                else status.HTTP_400_BAD_REQUEST
                                )

            if param == 'quick_books_customers':
                user = request.user
                result = handle_cutomer_quickbooks_csv_upload(
                    io_string=io_string, user=user)
                message = {
                    "message": ("Customers successfully added"
                                if result
                                else "No new customers added"),
                    "noOfCustomersAdded": result
                }
                return Response(message,
                                status.HTTP_201_CREATED
                                if result
                                else status.HTTP_400_BAD_REQUEST
                                )
            if param == 'batch_info':
                user = request.user
                handle_csv_object.handle_batch_csv_upload(user, io_string)
                message = {
                    "success": PRODUCTS_SUCCESS_RESPONSES[
                        "batch_upload_success"
                    ]
                }
                return Response(message, status.HTTP_201_CREATED)
            
            if param == 'stale_products':
                user = request.user
                result = handle_csv_object.unapprove_stale_product(user, io_string)
                message = {
                    "success": PRODUCTS_SUCCESS_RESPONSES[
                        "batch_upload_success"
                    ],
                    "noOfProductsFlagged": result,
                }
                return Response(message, status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise e



class HandleCsvExport(APIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, )
    serializer_class = ProductsSerializer

    def post(self, request, param):
        if param == 'products':
            limit = request.data.get('limit', None)
            query_set = Product.objects.filter(is_approved=True)[:limit]
            serializer = self.serializer_class(query_set, many=True)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = \
                'attachment; filename="products.csv"'
            headers = self.serializer_class.Meta.fields.copy()
            if request.data is not None:
                custom_headers = list()
                for key, value in request.data.items():
                    handle_csv_export.validate_request_data(
                        custom_headers, headers, key, value)
            headers = custom_headers if custom_headers else headers
            headers = \
                [handle_csv_export.capitalize(word) for word in headers]
            writer = csv.DictWriter(
                response,
                fieldnames=headers,
                extrasaction='ignore')
            writer.writeheader()
            for product in serializer.data:
                product = handle_csv_export.write_csv(product, request)
                writer.writerow(product)
            return response


class EmptyCsvFileExport(APIView):
    """Handle the download of empty CSV file"""
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated, )

    def get(self, request, param):
        """Responds to a get request for csv download based on the params
           with either products or customers or suppliers
        Args:
            request(obj): The http request from client.

        Returns:
            The response in a csv format with a status of 200.

        """
        if param == 'products':
            response = generate_csv_response(
                HttpResponse,
                'sample_product.csv',
                [Product],
                PRODUCT_INCLUDE_CSV_FIELDS)
        elif param == 'customers':
            response = generate_csv_response(
                HttpResponse,
                'sample_customers.csv',
                [Profile],
                CUSTOMERS_INCLUDE_CSV_FIELDS)
        elif param == 'batch_info':
            response = generate_csv_response(HttpResponse,
                                             'sample_batch_info.csv',
                                             [BatchInfo],
                                             BATCH_INFO_CSV_FIELDS,
                                             name='batch')
        elif param == 'suppliers':
            response = generate_csv_response(
                HttpResponse,
                'sample_suppliers.csv',
                [Suppliers,
                 SuppliersContacts,
                 SuppliersMeta],
                SUPPLIERS_INCLUDE_CSV_FIELDS)
        else:
            response = Response(ERROR_RESPONSES["wrong_param"],
                                status.HTTP_404_NOT_FOUND)
        return response
