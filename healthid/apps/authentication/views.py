import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.views import View

from healthid.apps.authentication.models import User
from healthid.utils.app_utils.validators import validate_password
from healthid.utils.auth_utils.tokens import account_activation_token
from healthid.utils.messages.authentication_responses import\
    AUTH_ERROR_RESPONSES, AUTH_SUCCESS_RESPONSES

FRONTEND_URL = settings.FRONTEND_URL
HTTP = settings.HTTP


def activate(request, uidb64, token):
    link = None
    template_type = None
    check_token, user = decode_token(uidb64, token)
    if check_token and user:
        user.is_active = True
        user.save()
        template_type = 'Email Verification Succeeded'
        message = AUTH_SUCCESS_RESPONSES["account_verification"]
        link = f'{HTTP}://{FRONTEND_URL}'
        status = 200  # success

    if not check_token and user:
        if user.is_active:
            template_type = 'Your email account has been verified successfully'
            message = AUTH_SUCCESS_RESPONSES["account_verification"]
            link = f'{HTTP}://{FRONTEND_URL}'
            status = 409  # conflict
        else:  # token may be expired
            message = AUTH_ERROR_RESPONSES["account_verification_fail"]
            status = 401  # unauthorised
    if not user and not check_token:  # token tampered with/corrupted
        # link tampered with
        message = AUTH_ERROR_RESPONSES["verification_link_corrupt"]
        status = 401
    context = {
        'template_type': template_type or 'Email Verification Failed',
        'small_text_detail': message,
        'link': link
    }
    return render(
        request, 'email_alerts/verification_fail.html',
        context=context, status=status)


class PasswordResetView(View):

    def get(self, request, uidb64, token):
        check_token, user = decode_token(uidb64, token)
        if check_token and user:
            return redirect(
                f'{HTTP}://{FRONTEND_URL}/reset_password/{uidb64}/{token}'
            )
        else:
            error = AUTH_ERROR_RESPONSES["reset_link_expiration"]
            context = {
                'template_type': 'Reseting password  failed',
                'small_text_detail': error,
                'link': f'{HTTP}://{FRONTEND_URL}/login'
            }
            return render(
                request, 'email_alerts/reset_password_fail.html',
                context=context, status=400)

    def put(self, request, uidb64, token):

        data = json.loads(request.body)
        check_token, user = decode_token(uidb64, token)
        if check_token and user:
            new_password = data.get('user').get('password')
            error = validate_password(new_password)
            if error:
                message = error
                status = 400
            else:
                user.set_password(new_password)
                user.save()
                message = AUTH_SUCCESS_RESPONSES["password_reset_success"]
                status = 200
            response = {"message": message}
            return JsonResponse(response, status=status)
        else:
            message = AUTH_ERROR_RESPONSES["verification_link_corrupt"]
            response = {"message": message}
        return JsonResponse(response, status=401)


def decode_token(uidb64, token):
    uid = force_bytes(urlsafe_base64_decode(uidb64)).decode('utf-8')
    try:
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        user = None
    check_token = account_activation_token.check_token(user, token)
    return check_token, user
