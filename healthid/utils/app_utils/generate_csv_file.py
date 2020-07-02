import csv
import io
import os


def generate_csv_file(file_name='file.csv', header=[], rows=[]):
    csv_file = None
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')

        writer.writerow(header)
        for row in rows:
            writer.writerow(row)

    with open(file_name, 'r') as file:
        data_set = file.read()
        csv_file = io.StringIO(data_set)

    os.remove(file_name)
    return csv_file
