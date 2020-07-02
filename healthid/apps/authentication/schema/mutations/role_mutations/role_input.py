import graphene


class RoleInput(graphene.InputObjectType):
    """
        Specifying the data types of the Role Input
    """

    id = graphene.String()
    name = graphene.String()
