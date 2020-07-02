from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.utils import timezone

from healthid.manager import BaseManager
from healthid.utils.app_utils.id_generator import ID_LENGTH, id_gen


class UserManager(BaseUserManager, BaseManager):
    def create_user(self, **kwargs):
        """
        Creates and saves a User with the given credentials.
        """
        email = kwargs.get("email")
        password = kwargs.get("password")
        mobile_number = kwargs.get("mobile_number")

        user = self.model.objects.filter(email=email).first()
        user_mobile_number = \
            self.model.objects.filter(mobile_number=mobile_number).first()
        if user_mobile_number:
            raise ValueError(
                "User with mobile number {mobile_number} "
                "already exists".format(mobile_number=mobile_number)
            )
        if user:
            raise ValueError(
                "User with email {email} already exists".format(email=email)
            )
        user = self.model(
            mobile_number=mobile_number, email=self.normalize_email(email)
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_superuser = user.is_staff = True
        user.is_active = user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
        User model
    """

    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=100, null=True, unique=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    secondary_email = models.EmailField(max_length=100, null=True, blank=True)
    secondary_phone_number = models.CharField(
        null=True, blank=True, max_length=100)
    profile_image = models.URLField(
        default='https://res.cloudinary.com/health-id/image/upload/'
        'v1554552278/Profile_Picture_Placeholder.png'
    )
    job_title = models.CharField(max_length=100, null=True, blank=True)
    starting_date = models.DateField(blank=True, null=True)
    birthday = models.DateField(auto_now=False, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    role = models.ForeignKey(
        "Role", related_name="role",
        null=True, blank=True,
        on_delete=models.CASCADE
    )
    is_staff = models.BooleanField(default=False)
    email_notification_permissions = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
    all_objects = UserManager(alive_only=False)

    def __str__(self):
        return self.email

    def has_admin_permission(self, perm, obj=None):
        return self.is_admin

    def has_module_permission(self, app_label):
        return self.is_admin

    def has_super_admin_permission(self, perm, obj=None):
        return self.is_superuser

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

    @property
    def active_outlet(self):
        """
        Method to return outlet user is active to

        Returns:
            outlet(obj): if user is active to an outlet
            None: if user is not active to any outlet
        """
        outlet_user = \
            self.outletuser_set.filter(is_default_outlet=True)
        if outlet_user.exists():
            return outlet_user.first().outlet
        outlet_user = \
            self.outletuser_set.filter(is_active_outlet=True)
        if outlet_user.exists():
            return outlet_user.first().outlet
        return None

    @property
    def active_outlets(self):
        """
        Method to return outlet user is active to

        Returns:
            outlet(obj): if user is active to an outlet
            None: if user is not active to any outlet
        """
        outlet_users = \
            self.outletuser_set.filter(is_active_outlet=True)
        active_outlets = []
        for outlet_user in outlet_users:
            active_outlets.append(outlet_user.outlet)
        if outlet_users.exists():
            return active_outlets
        return None

    @property
    def user_outlets(self):
        """
        Method to return outlets user belongs in

        Returns:
            list(obj): outlets user belongs in
        """
        return self.outlets.all()


class Role(models.Model):
    """
        User Role model
    """

    id = models.CharField(
        max_length=ID_LENGTH, primary_key=True, default=id_gen, editable=False
    )
    name = models.CharField(
        max_length=50, help_text="Enter Available Roles", unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    objects = BaseManager()
    all_objects = BaseManager(alive_only=False)

    class Meta:
        verbose_name_plural = "Roles"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()
