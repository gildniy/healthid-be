AUTH_SUCCESS_RESPONSES = {
    "registration_success": "You have successfully registered with healthID. ",
    "email_verification": "Please check your email to verify your account",
    "adding_new_user": "You have successfully registered {}",
    "updating_user": "Successfully updated {user_instance},"
                     "to {role_instance} role",
    "editing_user_role": "Successfully Edited the role",
    "login_success": "Login Successful",
    "password_reset_link_success": "Please check your email for a password"
                                   " reset link. Look inside your Spam folder"
                                   "in case you cannot trace it",
    "account_verification": "Your account is now verified,"
                            " Please click the button below to login",
    "password_reset_success": "Your password was successfully reset.",
    "create_role_success": "Successfully created a role: {}"
}

AUTH_ERROR_RESPONSES = {
    "assigning_user_roles": "This user is already assigned to this role",
    "downgrade_user": "You cannot downgrade this User,"
                      "This user is the only Master Admin, n this business",
    "login_validation_error": "Invalid login credentials",
    "authentication_error_response": "Please login to continue",
    "password_reset_blank_email": "Email address not found!.",
    "password_reset_invalid_email": "Please use the email you registered with",
    "account_verification_fail": "We could not verify your account, "
                                 "the verification link might have expired"
                                 " please contact your admin",
    "verification_link_corrupt": "This verification link is corrupted "
                                 "or expired",
    "email_verification_error": "{} has not been verified, please check your"
                                "inbox for a verification link",
    "password_match_error": "password does not match old password!",
    "email_duplicate_error": "email has already been registered.",
    "reset_link_expiration": "Reset link is expired or corrupted."
                             " Please request another.",
    "inexistent_role": "Role with id {} does not exist.",
    "special_characters_error": "{} must not contain special characters",
    "characters_exceed_error": "{} cannot exceed 30 characters",
    "short_password_error": "password must have at least 8 characters",
    "invalid_email_address": "{} is not a valid email address",
    "invalid_username": "valid username cannot be blank, "
                        "contain special characters "
                        "or exceed 30 characters.",
    "empty_role_name": "Role Field is empty"
}
