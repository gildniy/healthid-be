import csv


def generate_csv_response(response, filename, models=[],
                          include=[], name=None):
    """Generate an empty CSV file.

    The CSV file header is generated from the models fields and
    an include list is needed to explicitly state the field to
    be used

    Args:
        response (obj): The HttpResponse object.
        filename (str): The name of the csv file.
        models (cls): A list of names of the models to generate CSV
        include (list): The fields for the CSV column titles

    Returns:
        response (obj): The HttpResponse object.
    """

    header_row = []
    response = response(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename=' + filename

    for model in models:
        if name == 'batch':
            model_fields = [field.name for field in model._meta.get_fields()]
            header_row += [field.replace('_', ' ').title()
                           for field in include
                           if field in model_fields]
            header_row.insert(5, 'Quantity Received')
        else:
            header_row += [field.name.replace('_', ' ').title()
                           for field in model._meta.get_fields()
                           if field.name in include]

    writer = csv.DictWriter(
        response,
        fieldnames=header_row,
        extrasaction='ignore')
    writer.writeheader()

    return response
