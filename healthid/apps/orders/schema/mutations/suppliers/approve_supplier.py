import graphene
from django.core import serializers

from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.orders.schema.suppliers_query import SuppliersType
from healthid.apps.orders.models import Suppliers, SupplierRevisions, \
    SuppliersContacts, SuppliersMeta
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.apps.orders.models import SuppliersContacts as SuppliersContactsModel

class ApproveSupplier(graphene.Mutation):
    """
    Approve a new supplier

    args:
        id(str): id of the supplier to be approved

    returns:
        supplier(obj): 'Suppliers' model object detailing the approved
                       supplier.
        success(str): success message confirming approved supplier
    """

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Field(graphene.String)
    supplier = graphene.Field(SuppliersType)

    @classmethod
    @user_permission('Operations Admin')
    def mutate(cls, root, info, id):
        user = info.context.user
        supplier = get_model_object(Suppliers, 'id', id)
        supplier.is_approved = True
        name = supplier.name
        supplier.save()

        supplier_contacts_items = supplier.get_supplier_contacts
        supplier_contacts_model = SuppliersContactsModel()
        supplier_contacts = supplier_contacts_items[0]

        if supplier_contacts:
            for key in supplier_contacts.keys():
                supplier_contacts_model.__dict__[key] = supplier_contacts[key]

        supplier_meta = get_model_object(SuppliersMeta, 'supplier', supplier)

        revision = serializers.serialize(
                "json",
                [
                    supplier,
                    supplier_contacts_model,
                    supplier_meta
                ])
        SupplierRevisions.objects.create(
            proposed_by=user,
            version = revision,
            supplier=supplier,
            approved_by=user,
            is_approved=True,
            status="active")

        success = SUCCESS_RESPONSES[
            "approval_success"].format("Supplier" + name)
        return cls(success=success, supplier=supplier)
