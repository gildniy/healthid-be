import graphene

# mutations
from .mutations.auth_mutations.register_user import RegisterUser
from .mutations.auth_mutations.add_user import AddUser
from .mutations.auth_mutations.admin_update_user import AdminUpdateUserDetails
from .mutations.auth_mutations.update_user import UpdateUserDetails
from .mutations.auth_mutations.update_admin_user import UpdateAdminUser
from .mutations.auth_mutations.login_mutation import LoginUser
from .mutations.auth_mutations.reset_password_mutation import ResetPassword
from .mutations.role_mutations.create import CreateRole
from .mutations.role_mutations.update import UpdateUserRole
from .mutations.role_mutations.edit import EditRole
from .mutations.role_mutations.delete import DeleteRole


class Mutation(graphene.ObjectType):
    # user
    add_user = AddUser.Field()
    create_user = RegisterUser.Field()
    update_user = UpdateUserDetails.Field()
    update_admin_user = UpdateAdminUser.Field()
    admin_update_user = AdminUpdateUserDetails.Field()
    login_user = LoginUser.Field()
    reset_password = ResetPassword.Field()
    # role
    create_role = CreateRole.Field()
    update_role = UpdateUserRole.Field()
    edit_role = EditRole.Field()
    delete_role = DeleteRole.Field()
