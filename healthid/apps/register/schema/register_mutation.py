import graphene
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.utils.auth_utils.decorator import user_permission
from healthid.apps.outlets.models import Outlet
from healthid.apps.receipts.models import ReceiptTemplate
from healthid.apps.register.models import Register
from healthid.apps.register.schema.register_schema import RegisterType
from healthid.utils.app_utils.database import (SaveContextManager,
                                               get_model_object)
from healthid.utils.messages.register_responses import REGISTER_ERROR_RESPONSES
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES
from healthid.utils.registers.registers import generate_register_id


class RegisterInput(graphene.InputObjectType):

    id = graphene.String()
    name = graphene.String()


class CreateRegister(graphene.Mutation):
    """
    This Creates a register
    """
    registers = graphene.List(RegisterType)
    message = graphene.Field(graphene.String)

    class Arguments:
        name = graphene.String(required=True)
        outlet_id = graphene.Int(required=True)
        number = graphene.Int(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        register_name = kwargs.get('name')
        number = kwargs.get('number')
        outlet = get_model_object(Outlet, 'id', kwargs.get('outlet_id'))

        registers = []
        if register_name.strip() != "":
            for i in range(number):
                most_recent_register_created = Register.original_objects.filter(
                    original_name=register_name,
                    deleted_at=None
                ).order_by('-created_at').first()
                if most_recent_register_created:
                    higest_register_number = int(most_recent_register_created.name.split(" ")[1])
                else:
                    higest_register_number = 0

                register = Register(
                    name=register_name + ' ' + str(higest_register_number + 1),
                    outlet_id=outlet.id,
                    original_name=register_name,
                )
                
                with SaveContextManager(register, model=Register) as register:
                    register.register_id = generate_register_id(
                        outlet, register.id)
                    register.save()
                    registers.append(register)
            success_message = SUCCESS_RESPONSES["creation_success"].format(
                "Register")
            return CreateRegister(registers=registers, message=success_message)

        raise GraphQLError(
            REGISTER_ERROR_RESPONSES[
                "invalid_register_name_error"].format(register_name))


class UpdateRegister(graphene.Mutation):
    """
    This Updates a register
    """
    errors = graphene.List(graphene.String)
    message = graphene.Field(graphene.String)
    success = graphene.Boolean()
    register = graphene.Field(RegisterType)

    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String(required=True)

    @login_required
    @user_permission()
    def mutate(self, info, id, name):
        register = get_model_object(Register, 'id', id)
        if name.strip() != "":
            register.name = name
            register.save()
            success_message = SUCCESS_RESPONSES["update_success"].format(
                "Register")
            return UpdateRegister(
                message=success_message,
                register=register,
                success=True
            )
        raise GraphQLError(
            REGISTER_ERROR_RESPONSES[
                "invalid_register_name_error"].format(name))


class DeleteRegister(graphene.Mutation):
    """
    This Deletes a register
    """
    id = graphene.Int()
    message = graphene.String()
    success = graphene.String()

    class Arguments:
        id = graphene.Int()

    @login_required
    @user_permission()
    def mutate(self, info, id):
        user = info.context.user
        register = get_model_object(Register, 'id', id)
        register.delete(user)
        return DeleteRegister(
            success=SUCCESS_RESPONSES[
                "deletion_success"].format("Register"))

class DeleteMultipleRegisters(graphene.Mutation):
    """
    This deletes multiple registers
    """
    success = graphene.String()

    class Arguments:
        ids = graphene.List(graphene.Int, required=True)

    @login_required
    @user_permission()
    def mutate(self, info, **kwargs):
        ids = kwargs.get('ids')
        user = info.context.user

        for id in ids:
            register = get_model_object(Register, 'id', id)
            register.delete(user)

        return DeleteMultipleRegisters(
            success=SUCCESS_RESPONSES[
                "deletion_success"].format("Registers"))

class Mutation(graphene.ObjectType):
    create_register = CreateRegister.Field()
    delete_register = DeleteRegister.Field()
    delete_registers = DeleteMultipleRegisters.Field()
    update_register = UpdateRegister.Field()
