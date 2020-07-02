import graphene
from django.forms.models import model_to_dict
from django.core import serializers
from graphql import GraphQLError

from healthid.apps.orders.models import Suppliers, SuppliersContacts,\
    SuppliersMeta, SupplierRevisions
from healthid.apps.orders.models.suppliers import SupplierOutletContacts
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.app_utils.get_user_business import get_user_business
from healthid.apps.orders.schema.suppliers_query import SuppliersType
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES


class ApproveEditRequest(graphene.Mutation):
    """
    Approve an edit to a supplier's details

    args:
        id(str): id of the supplier to be edited

    returns:
        supplier(obj): 'Suppliers' model object detailing the edit request
        message(str): success message confirming supplier edit approval
    """

    class Arguments:
        id = graphene.String(required=True)

    message = graphene.Field(graphene.String)
    supplier = graphene.Field(SuppliersType)

    @classmethod
    @user_permission('Operations Admin')
    def mutate(cls, root, info, **kwargs):
        id = kwargs.get('id')
        user = info.context.user
        user_business = get_user_business(user)
        supplier_revision = get_model_object(SupplierRevisions, 'id', id)

        if not supplier_revision:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES[
                    "supplier_revision_not_found"].format(id))

        deserialized_revision = serializers.deserialize("json", supplier_revision.version)
        revision_business = supplier_revision.supplier.business.all().first()

        if revision_business.id != user_business.id:
            raise GraphQLError(
                ORDERS_ERROR_RESPONSES[
                    "supplier_revision_not_allowed"])

        supplier = next(deserialized_revision)
        supplier_contacts = next(deserialized_revision)
        supplier_meta = next(deserialized_revision)

        supplier.save()
        supplier_meta.save()

        supplier_id = supplier.object.id
        outlet_id = supplier_contacts.object.outlet.id
        contacts = SupplierOutletContacts.objects.filter(supplier_id=supplier_id, outlet_id=outlet_id)
        updated_contacts_keys = supplier_contacts.object.__dict__.keys()

        for contact in contacts:
            key = contact.__dict__['dataKey']
            if key in updated_contacts_keys:
                contact.__dict__["dataValue"] = supplier_contacts.object.__dict__[key]
                contact.save()

        supplier_revision.status = "active"
        supplier_revision.approved_by = user
        supplier_revision.is_approved = True
        supplier_revision.save()

        supplier = Suppliers.objects.get(id=supplier_revision.supplier.id)
        other_revisions = SupplierRevisions.objects.filter(
            supplier=supplier_revision.supplier).exclude(id=id)

        for revision_item in other_revisions:
            revision_item.status = "inactive"
            revision_item.save()

        message = SUCCESS_RESPONSES["update_success"].format(f"Supplier {supplier.name}")
        return cls(message, supplier)
