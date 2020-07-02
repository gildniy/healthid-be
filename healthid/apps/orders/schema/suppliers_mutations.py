import graphene

from healthid.apps.orders.schema.mutations.suppliers.add_supplier \
    import AddSupplier
from healthid.apps.orders.schema.mutations.suppliers.add_supplier_contacts \
    import AddSupplierContacts
from healthid.apps.orders.schema.mutations.suppliers.add_supplier_meta\
    import AddSupplierMeta
from healthid.apps.orders.schema.mutations.suppliers.approve_supplier \
    import ApproveSupplier
from healthid.apps.orders.schema.mutations.suppliers.delete_supplier \
    import DeleteSupplier
from healthid.apps.orders.schema.mutations.suppliers.edit_supplier \
    import EditSupplier
from healthid.apps.orders.schema.mutations.suppliers.edit_supplier_contacts \
    import EditSupplierContacts
from healthid.apps.orders.schema.mutations.suppliers.edit_supplier_meta \
    import EditSupplierMeta
from healthid.apps.orders.schema.mutations.suppliers.edit_proposal \
    import EditProposal
from healthid.apps.orders.schema.mutations.suppliers.approve_edit_request \
    import ApproveEditRequest
from healthid.apps.orders.schema.mutations.suppliers.decline_edit_request \
    import DeclineEditRequest
from healthid.apps.orders.schema.mutations.suppliers.create_suppliernote \
    import CreateSupplierNote
from healthid.apps.orders.schema.mutations.suppliers.update_suppliernote \
    import UpdateSupplierNote
from healthid.apps.orders.schema.mutations.suppliers.delete_suppliernote \
    import DeleteSupplierNote
from healthid.apps.orders.schema.mutations.suppliers.rate_supplier \
    import RateSupplier


class Mutation(graphene.ObjectType):
    add_supplier = AddSupplier.Field()
    add_supplier_contacts = AddSupplierContacts.Field()
    add_supplier_meta = AddSupplierMeta.Field()
    approve_supplier = ApproveSupplier.Field()
    delete_supplier = DeleteSupplier.Field()
    edit_supplier = EditSupplier.Field()
    edit_supplier_contacts = EditSupplierContacts.Field()
    edit_supplier_meta = EditSupplierMeta.Field()
    edit_proposal = EditProposal.Field()
    approve_edit_request = ApproveEditRequest.Field()
    decline_edit_request = DeclineEditRequest.Field()
    create_suppliernote = CreateSupplierNote.Field()
    update_suppliernote = UpdateSupplierNote.Field()
    delete_suppliernote = DeleteSupplierNote.Field()
    rate_supplier = RateSupplier.Field()
