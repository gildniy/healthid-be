from os import environ, getenv
import graphene
import cloudinary
import cloudinary.api
import cloudinary.uploader
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from graphql_jwt.decorators import login_required


from healthid.apps.authentication.schema.types.user_type import UserType
from healthid.apps.authentication.models import Role, User
from healthid.utils.app_utils.database import get_model_object
from healthid.utils.auth_utils.tokens import account_activation_token
from healthid.utils.app_utils.send_mail import SendMail
from healthid.utils.messages.authentication_responses import (
    AUTH_SUCCESS_RESPONSES)
from healthid.utils.auth_utils.decorator import user_permission
from healthid.utils.auth_utils import user_update_instance
from healthid.apps.outlets.models import Outlet, OutletUser
from healthid.utils.auth_utils.password_generator import generate_password
from healthid.apps.business.models import UserBusiness
from healthid.apps.business.models import Business


DOMAIN = environ.get('DOMAIN') or getenv('DOMAIN')


class AddUser(graphene.Mutation):
    """
        Mutation to register a user.
    """
    user = graphene.Field(UserType)
    verification_link = graphene.Field(graphene.String)

    class Arguments:
        outlet_id = graphene.List(graphene.String, required=True)
        email = graphene.String(required=True)
        mobile_number = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        username = graphene.String()
        profile_image = graphene.String()
        job_title = graphene.String()
        starting_date = graphene.String()
        birthday = graphene.String()
        role_id = graphene.String(required=True)

    success = graphene.List(graphene.String)
    errors = graphene.List(graphene.String)

    @login_required
    @user_permission()
    @user_update_instance
    def mutate(self, info, **kwargs):
        password = generate_password()
        email = kwargs.get('email')
        mobile_number = kwargs.get('mobile_number')
        outlet = kwargs.get('outlet_id')
        role_id = kwargs.get('role_id')
        profile_image = kwargs.get('profile_image')

        data = {
            'first_name': kwargs.get('first_name'),
            'last_name': kwargs.get('last_name'),
            'username': kwargs.get('username'),
            'job_title': kwargs.get('job_title'),
            'starting_date': kwargs.get('starting_date'),
            'birthday': kwargs.get('birthday'),
        }

        role_instance = get_model_object(Role, 'id', role_id)
        try:
            user_fields = {
                "email": email,
                "password": password,
                "mobile_number": mobile_number
            }
            user = User.objects.create_user(**user_fields)
            user_update_instance.add_user(user, **data)
            user.role = role_instance
            for outlet_id in outlet:
                outlet_instance = get_model_object(Outlet, 'id', outlet_id)
                business_instance = outlet_instance.business
                business_instance.user = user
                is_active_outlet = False if user.user_outlets.exists() \
                    else True
                OutletUser.objects.create(user=user,
                                          outlet=outlet_instance,
                                          is_active_outlet=is_active_outlet)
            if profile_image:
                user.profile_image = \
                    cloudinary.uploader.upload(profile_image).get('url')
            user.save()
            # Email verification
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
                'small_text_detail': ' A HealthID account has been created '
                                     'for you. Please verify your email '
                                     'address to set up your account.',
                'email': email,
                'domain': DOMAIN,
                'uid': uid,
                'token': token,
                'password': password
            }
            send_mail = SendMail(
                email_verify_template, context, subject, to_email)
            send_mail.send()
            verification_link = f"{DOMAIN}/healthid/activate/{uid}/{token}"
            add_user_message =\
                AUTH_SUCCESS_RESPONSES["adding_new_user"].format(user.username)
            success = [
                add_user_message
            ]

            business = get_model_object(Business, 'user_id', info.context.user.id)

            user_business = UserBusiness()
            user_business.user = user
            user_business.business = business
            user_business.save()

            return AddUser(success=success, user=user,
                           verification_link=verification_link)
        except Exception as e:
            errors = ['Something went wrong: {}'.format(e)]
            return AddUser(errors=errors)
