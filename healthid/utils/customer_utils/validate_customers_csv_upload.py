import csv
from rest_framework.exceptions import ValidationError

from healthid.utils.messages.common_responses import ERROR_RESPONSES


def validate_customers_csv_upload(io_string):
    """
        Validate customers info from an appropriately formatted CSV file.

        arguments:
            io_string(obj): 'io.StringIO' object containing a list
                            of customers in CSV format

        returns:
            array: a list of customers
        """
    [row_count, csv_columns, customers, csv_errors] = [0, [], [], {}]
    valid_columns = {
        'first name': 'not required',
        'last name': 'not required',
        'email': 'not required',
        'city': 'not required',
        'country': 'not required',
        'primary mobile number': 'required',
        'secondary mobile number': 'not required',
        'loyalty member': 'not required',
        'loyalty points': 'not required',
        'region': 'not required',
        'address line 1': 'not required',
        'address line 2': 'not required',
        'emergency contact name': 'not required',
        'emergency contact number': 'not required',
        'emergency contact email': 'not required',
        'last sale dt': 'not required',
        'lty lvl': 'not required',
        'lty opt in': 'not required',
        'lty enroll date': 'not required',
        'prc lvl': 'not required',
        'str credit': 'not required'
    }

    for row in csv.reader(io_string):
        csv_columns = list(map(lambda column: column.lower().strip(), row))
        break

    for column in csv_columns:
        csv_errors = {
            **csv_errors,
            'columns': [
                *(csv_errors.get('column') or []),
                ERROR_RESPONSES['not_allowed_column'].format(column)
            ]
        } if column.lower().strip() not in valid_columns else csv_errors

    for row in csv.reader(io_string):
        row_count += 1
        [i, customer, row_errors] = [0, {}, {}]
        while i < len(row):
            if valid_columns.get(csv_columns[i]) == 'required' and not row[i]:
                row_errors = {
                    **row_errors,
                    csv_columns[i]: ERROR_RESPONSES['required_field'].format(
                        csv_columns[i])
                }

            customer = {
                **customer,
                csv_columns[i]: row[i]
            } if csv_columns[i] else customer

            i += 1

        csv_errors = {
            **csv_errors,
            'rows': [
                *(csv_errors.get('rows') or {}),
                {f'{row_count}': row_errors}
            ]
        } if len(row_errors) else csv_errors

        customers = [*customers, customer]

    if len(csv_errors):
        raise ValidationError({
            "error": csv_errors})

    return customers
