from functools import wraps
from graphql import GraphQLError
from graphql.execution.base import ResolveInfo


def user_permission(*param):
    allowed_role = ['Master Admin']
    for arg in param:
        allowed_role.append(arg)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            info = [arg for arg in args if isinstance(arg, ResolveInfo)]
            user = info[0].context.user
            if str(user.role) in allowed_role:
                return f(*args, **kwargs)
            raise GraphQLError(
                "Permission denied. You don't "
                "have access to this functionality"
            )

        return wrapper
    return decorator
