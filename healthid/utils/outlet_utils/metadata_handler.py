from healthid.apps.outlets.models import OutletMeta, OutletContacts

outlet_meta_object = {
    "date_launched": "",
    "prefix_id": ""
}

outlet_contacts_object = {
    "address_line1": "",
    "address_line2": "",
    "lga": "",
    "phone_number": ""
}


def add_outlet_metadata(outlet, items):
    for (key, value) in items:
        if key in outlet_meta_object and value:
            OutletMeta.objects.create(
                outlet=outlet, dataKey=key, dataValue=value
            )
        elif key in outlet_contacts_object and value:
            OutletContacts.objects.create(
                outlet=outlet, dataKey=key, dataValue=value
            )


def update_outlet_metadata(outlet, items):
    for (key, value) in items:
        if key in outlet_meta_object and value:
            outlet_meta_filter = OutletMeta.objects.filter(
                outlet=outlet, dataKey__icontains=key)
            if len(outlet_meta_filter) > 0:
                outlet_meta_filter[0].dataValue = value
                outlet_meta_filter[0].save()
        elif key in outlet_contacts_object and value:
            outlet_contact_filter = OutletContacts.objects.filter(
                outlet=outlet, dataKey__icontains=key)
            if len(outlet_contact_filter) > 0:
                outlet_contact_filter[0].dataValue = value
                outlet_contact_filter[0].save()
            else:
                OutletContacts.objects.create(
                    outlet=outlet, dataKey=key, dataValue=value
                )
