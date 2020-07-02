from healthid.utils.app_utils.validator import validator


class ValidateUser():
    """
    User's fields validations

    parameters:
        email(str): user's email
        password(str): user's password
        mobile_number(str): user's mobile number
    """
    def validate_user_fields(self, email, password, mobile_number):
        return {
            "email": validator.validate_email(email),
            "mobile_number": validator.validate_mobile(mobile_number),
            "password": validator.validate_password(password)
        }
