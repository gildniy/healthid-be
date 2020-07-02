from os import environ, getenv

import graphene
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from graphql import GraphQLError

from healthid.apps.authentication.models import User
from healthid.utils.auth_utils.tokens import account_activation_token
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.messages.authentication_responses import\
    AUTH_ERROR_RESPONSES, AUTH_SUCCESS_RESPONSES
DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class ResetPassword(graphene.Mutation):
    """
    Functions of this mutation class:
    1. Receive user email and check that user exists.
    2. Generate a token for resetting password.
    3. Create a reset password link using the token.
    4. Send the user a password reset email.
    """
    reset_link = graphene.Field(graphene.String)
    success = graphene.Field(graphene.String)

    class Arguments:
        email = graphene.String(required=True)

    def mutate(self, info, email):
        if email.strip() == "":
            blank_email = AUTH_ERROR_RESPONSES["password_reset_blank_email"]
            raise GraphQLError(blank_email)

        user = User.objects.filter(email=email).first()
        if user is None:
            invalid_email = AUTH_ERROR_RESPONSES["password_reset_blank_email"]
            raise GraphQLError(invalid_email)

        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(
            user.pk))
        user_firstname = user.first_name
        if not user_firstname:
            user_firstname = "User"

        # Send email to the user
        to_email = [
            user.email
        ]
        email_verify_template = \
            'email_alerts/authentication/password_reset_email.html'
        subject = 'Password Reset'
        context = {
            'template_type': 'Password reset requested '
                             'for your HealthID Account.',
            'small_text_detail': '',
            'name': user_firstname,
            'email': email,
            'domain': DOMAIN,
            'uid': uid,
            'token': token,
        }
        send_mail = SendMail(
            email_verify_template, context, subject, to_email)
        send_mail.send()

        reset_link = "{}/healthid/password_reset/{}/{}".format(
            DOMAIN, uid, token)
        success = AUTH_SUCCESS_RESPONSES["password_reset_link_success"]

        return ResetPassword(reset_link=reset_link, success=success)
