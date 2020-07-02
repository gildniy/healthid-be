import graphene


class PasswordInput(graphene.InputObjectType):
    new_password = graphene.String()
    old_password = graphene.String()
