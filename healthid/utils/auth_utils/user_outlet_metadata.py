from healthid.apps.outlets.models import Outlet
from healthid.utils.app_utils.database import get_model_object


def merge_metadata_to_user_outlet_object(active_outlet_id):
    outlet = get_model_object(Outlet, 'id', active_outlet_id)
    outlets_meta = outlet.outletmeta_set.all()
    outlets_contact = outlet.outletcontacts_set.all()
    for outlet_meta in outlets_meta:
        if outlet.id == outlet_meta.__dict__['outlet_id']:
            outlet.__dict__[outlet_meta.__dict__[
                'dataKey']] = outlet_meta.__dict__['dataValue']
        else:
            outlet.__dict__[outlet_meta.__dict__['dataKey']] = None
    for outlet_contact in outlets_contact:
        if outlet.id == outlet_contact.__dict__['outlet_id']:
            outlet.__dict__[outlet_contact.__dict__[
                'dataKey']] = outlet_contact.__dict__['dataValue']
        else:
            outlet.__dict__[outlet_contact.__dict__['dataKey']] = None

    return outlet
