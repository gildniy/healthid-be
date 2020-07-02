import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from healthid.apps.register.models import Register
from healthid.utils.app_utils.database import get_model_object


class RegisterType(DjangoObjectType):
    class Meta:
        model = Register


class Query(graphene.ObjectType):
    """
    Return a list of registers.
    Or return a single register specified.
    """

    registers = graphene.List(RegisterType)
    register = graphene.Field(RegisterType, id=graphene.Int())

    @login_required
    def resolve_registers(self, info, **kwargs):
        return Register.objects.all()

    @login_required
    def resolve_register(self, info, **kwargs):
        id = kwargs.get('id')
        register = get_model_object(Register, 'id', id)
        return register
