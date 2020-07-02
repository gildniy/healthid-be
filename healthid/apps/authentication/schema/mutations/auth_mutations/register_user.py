from healthid.utils.auth_utils.validations import ValidateUser
import graphene
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from os import environ, getenv
from healthid.apps.authentication.schema.types.user_type import UserType
from healthid.apps.authentication.models import Role, User
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.tokens import account_activation_token
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.messages.authentication_responses import (
    AUTH_SUCCESS_RESPONSES)

DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class RegisterUser(graphene.Mutation):
    """
        Mutation to register a user.
    """
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        mobile_number = graphene.String(required=True)

    success = graphene.List(graphene.String)
    errors = graphene.List(graphene.String)
    verification_link = graphene.Field(graphene.String)

    def mutate(self, info, email, password, mobile_number):
        mobile_number = mobile_number.replace(" ", "")
        validate_fields = ValidateUser().validate_user_fields(
            email, password, mobile_number)
        try:
            user = User.objects.create_user(**validate_fields)
            role = get_model_object(Role, 'name', 'Master Admin')
            user.set_password(password)
            user.role = role
            user.save()
            # account verification
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(
                user.pk))
            to_email = [
                user.email
            ]
            email_verify_template = \
                'email_alerts/authentication/verification_email.html'
            subject = 'Account Verification'
            context = {
                'template_type': 'Verify your email',
                'small_text_detail': 'Thank you for '
                                     'creating a HealthID account. '
                                     'Please verify your email '
                                     'address to set up your account.',
                'email': user.email,
                'password': password,
                'domain': DOMAIN,
                'uid': uid,
                'token': token,
            }
            send_mail = SendMail(
                email_verify_template, context, subject, to_email)
            send_mail.send()
            registration_message =\
                AUTH_SUCCESS_RESPONSES["registration_success"]
            verification_message = AUTH_SUCCESS_RESPONSES["email_verification"]

            success = [
                registration_message + verification_message
            ]
            verification_link = f"{DOMAIN}/healthid/activate/{uid}/{token}"
            return RegisterUser(success=success, user=user,
                                verification_link=verification_link)
        except Exception as e:
            errors = ["Something went wrong: {}".format(e)]
            return RegisterUser(errors=errors)
