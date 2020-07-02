import csv
from rest_framework.exceptions import ValidationError, NotFound
from healthid.utils.app_utils.database import (
    SaveContextManager, get_model_object)
from healthid.apps.profiles.models import Profile
from healthid.apps.outlets.models import City, Country
from healthid.utils.customer_utils.validate_customers_csv_upload import (
    validate_customers_csv_upload)
from healthid.utils.customer_utils.customer_meta_handler import (
    add_customer_metadata)
from healthid.utils.app_utils.validator import validator
from healthid.apps.business.models import Business
from healthid.utils.app_utils.get_user_business import get_user_business


class HandleCustomerCSVValidation:
    def handle_customer_csv_upload(self, io_string, user):
        """
        This CSV method loops through the csv file populating the DB with
        the information in the csv rows through the SaveContextManager,
        :param io_string:
        :return total number pf csv rows uploaded into the DB:
        The columns of the csv file must be in a PARTICULAR order to ease
        the upload process
        """
        params = {'model': Profile, 'error_type': ValidationError}
        [customer_count, row_count] = [0, 0]
        customers = validate_customers_csv_upload(io_string)
        business_id = get_user_business(user).id
        for row in customers:
            row_count += 1
            customer_profile_instance = Profile(
                business_id=business_id,
                first_name=row.get('first name').title(),
                last_name=row.get('last name').title(),
                email=(
                    row.get('email')).replace(
                    '"',
                    ''),
                city=get_model_object(City,
                                      'name__iexact',
                                      row.get('city'),
                                      error_type=NotFound,
                                      label='name')
                if row.get('city') else None,
                country=get_model_object(Country,
                                         'name__iexact',
                                         row.get('country'),
                                         error_type=NotFound,
                                         label='name')
                if row.get('country') else None,
                primary_mobile_number=row.get('primary mobile number'),
                secondary_mobile_number=row.get('secondary mobile number'),
                loyalty_points=row.get('loyalty points'),
                local_government_area=(
                    row.get('region')).replace(
                    '"',
                    ''),
                address_line_1=row.get('address line 1'),
                address_line_2=row.get('address line 2'),
                emergency_contact_name=(
                    row.get('emergency contact name')).replace(
                    '"',
                    ''),
                emergency_contact_number=row.get('emergency contact number'),
                emergency_contact_email=row.get('emergency contact email'))
            business_id = get_user_business(user).id
            check_profile_dublicates = Profile.objects.filter(
                primary_mobile_number=customer_profile_instance.
                primary_mobile_number
            ).filter(business_id=business_id)
            check_email_duplicate = Profile.objects.filter(business_id=business_id, email=customer_profile_instance.email)
            if len(check_email_duplicate):
                error = "Email {} on row {} already exists"
                raise ValidationError(
                    {'error': error.format(customer_profile_instance.email,
                                           row_count)})
            valid_email = validator.validate_email(
                customer_profile_instance.email)
            if not check_profile_dublicates and valid_email:
                with SaveContextManager(customer_profile_instance, **params):
                    pass

                customer_count += 1

        return customer_count

    def handle_cutomer_retail_pro_csv_upload(self, io_string, user):
        """
        Maps customers information from a retail pro csv file to a Health ID
        formatted CSV file
        and save them.
        arguments:
            io_string(obj): 'io.StringIO' object containing a list
                            of customers in CSV format
        returns:
            int: the number of saved customers
        """
        customer_count = 0
        duplicates_count = 0
        for row in csv.DictReader(io_string):
            last = ((row.get('Last')).replace('"', '')).title()
            first = ((row.get('First')).replace('"', '')).title()
            phone1 = row.get('Phone1')
            phone2 = row.get('Phone2')
            last_sale_dt = row.get('Last Sale Dt')
            str_credit = row.get('Str Credit')
            lty_lvl = row.get('Lty Lvl')
            lyt_opt_in = row.get('Lty Opt in')
            lty_balance = row.get('Lty Balance')
            lty_enroll_date = (row.get('Lty Enroll Date')).replace('"', '')
            prc_lvl = row.get('Prc Lvl')
            loyalty_member = True

            customer_meta_args = {
                'last_sale_dt': last_sale_dt,
                'lty_lvl': lty_lvl,
                'lyt_opt_in': lyt_opt_in,
                'lty_enroll_date': lty_enroll_date,
                'prc_lvl': prc_lvl,
                'str_credit': str_credit
            }

            if not lty_enroll_date:
                loyalty_member = False
            business_id = get_user_business(user).id
            check_profile_dublicates = Profile.objects.filter(
                primary_mobile_number=phone1,
                first_name=first,
                last_name=last
                ).filter(
                business_id=business_id
                )
            if not check_profile_dublicates:
                customer = Profile.objects.create(
                    business_id=business_id,
                    first_name=first,
                    last_name=last,
                    primary_mobile_number=phone1,
                    secondary_mobile_number=phone2,
                    loyalty_member=loyalty_member,
                    loyalty_points=lty_balance,
                    city=get_model_object(City,
                                          'name__iexact',
                                          "Lagos",
                                          error_type=NotFound,
                                          label='name')
                    if "Lagos" else None,
                    country=get_model_object(Country,
                                             'name__iexact',
                                             "Nigeria",
                                             error_type=NotFound,
                                             label='name')
                    if "Nigeria" else None,
                )
                add_customer_metadata(customer, customer_meta_args)
                customer_count += 1
            else:
                duplicates_count += 1

        return customer_count, duplicates_count

    def handle_cutomer_quickbooks_csv_upload(self, io_string, user):
        """
        Maps customers information from quickbooks to Health ID
        formatted CSV file
        and save them.
        arguments:
            io_string(obj): 'io.StringIO' object containing a list
                            of customers in CSV format
        returns:
            int: the number of saved customers
        """
        customer_count = 0
        for row in csv.DictReader(io_string):
            title = (row.get('Title')).title()
            first_name = (row.get('First Name')).title()
            last_name = (row.get('Last Name')).title()
            customer_type = row.get('Customer Type')
            phone1 = row.get('Phone 1')
            phone2 = row.get('Phone 2')
            email = row.get('EMail').replace(' ', '').replace('_', '')
            disc = row.get('Disc %')
            last_Sale = row.get('Last Sale')
            user_type = 0

            customer_quicks_meta_args = {
                'title': title,
                'customer_type': customer_type,
                'disc': disc,
                'last_Sale': last_Sale
            }

            if email == "":
                email = None

            if customer_type == "":
                user_type = 0
            business_id = get_user_business(user).id
            check_profile_dublicates = Profile.objects.filter(
                    primary_mobile_number=phone1
                ).filter(
                    business_id=business_id
                )
            if not check_profile_dublicates:
                customer_quickbooks = Profile.objects.create(
                    business_id=business_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    user_type=user_type,
                    primary_mobile_number=phone1,
                    secondary_mobile_number=phone2,
                    city=get_model_object(City,
                                          'name__iexact',
                                          "Lagos",
                                          error_type=NotFound,
                                          label='name')
                    if "Lagos" else None,
                    country=get_model_object(Country,
                                             'name__iexact',
                                             "Nigeria",
                                             error_type=NotFound,
                                             label='name')
                    if "Nigeria" else None,
                )
                add_customer_metadata(
                    customer_quickbooks, customer_quicks_meta_args)
                customer_count += 1

        return customer_count
