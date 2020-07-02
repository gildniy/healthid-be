def format_supplier_csv_file_info(row, key, default_value):
    return row.get(key) and row.get(key).replace('"', '').capitalize() or default_value


def upload_supplier_quickbook_csv_file(row, user):
    return [
        format_supplier_csv_file_info(row, 'Company', 'N/A'),
        format_supplier_csv_file_info(row, 'E-Mail', 'N/A'),
        row.get('Phone1') or '+2359094444',
        user.active_outlet.business.country,
        format_supplier_csv_file_info(row, 'Addr1', 'N/A'),
        format_supplier_csv_file_info(row, 'Addr2', 'N/A'),
        format_supplier_csv_file_info(row, 'Addr3', 'N/A'),
        user.active_outlet.business.city,
        row.get('Tier') or '3t+ wholesaler',
        'N/A',
        'N/A',
        'cash on delivery',
        0,
        True

    ]
