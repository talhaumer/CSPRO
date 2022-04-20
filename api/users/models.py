""" Models of user module."""
from builtins import ValueError
from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, Group, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.text import slugify
from model_utils import Choices

from api.zone.models import Countries, Zone
from main.models import Base


class AccessLevel:
    """
    Access levels for user roles.
    """

    SALES_MANAGER = 200
    LOCAL_ADMIN = 800
    SUPER_ADMIN = 900
    PROCTOR = 300

    SALES_MANAGER_CODE = "sales_manager"
    LOCAL_ADMIN_CODE = "local_admin"
    SUPER_ADMIN_CODE = "super_admin"
    PROCTOR_CODE = "proctor"

    CHOICES = (
        (SALES_MANAGER, "Sales_Manager"),
        (LOCAL_ADMIN, "Local_Admin"),
        (SUPER_ADMIN, "Super_Admin"),
        (PROCTOR, "Proctor"),
    )

    CODES = (
        (SALES_MANAGER, "sales_manager"),
        (LOCAL_ADMIN, "local-admin"),
        (SUPER_ADMIN, "super-admin"),
        (PROCTOR, "proctor"),
    )

    DICT = dict(CHOICES)
    CODES_DICT = dict(CODES)


class Role(Base):
    """Role model."""

    name = models.CharField(db_column="Name", max_length=255, unique=True)
    code = models.SlugField(db_column="Code", default="")
    description = models.TextField(db_column="Description", null=True, blank=True)
    access_level = models.IntegerField(
        db_column="AccessLevel",
        choices=AccessLevel.CHOICES,
        default=AccessLevel.SALES_MANAGER,
    )

    class Meta:
        db_table = "Roles"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.code = slugify(self.name)
            super().save()
        except Exception:
            raise

    def get_role_by_code(self=None, code=None):
        try:
            return Role.objects.get(code__exact=code)
        except Exception as e:
            print(e)
            return e


class CustomAccountManager(BaseUserManager):
    def create_user(self, email, password):
        user = self.model(email=email, password=password)
        user.role = Role.objects.get(code="super_admin")
        user.set_password(password)
        user.is_superuser = False
        user.is_approved = False
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_approved = True
        user.is_active = True
        user.role = Role.objects.get(code="super_admin")
        user.save()
        return user


class User(AbstractBaseUser, Base, PermissionsMixin):
    """User model."""

    name = models.CharField(db_column="Name", default="", max_length=255)
    is_active = models.BooleanField(
        db_column="IsActive",
        default=True,
        help_text="Designates whether this user should be treated as active.",
    )
    email = models.EmailField(unique=True, db_column="Email", help_text="Email Field")
    image = models.ImageField(
        upload_to="uploads/", db_column="ImageField", null=True, blank=True
    )
    is_approved = models.BooleanField(
        db_column="IsApproved",
        default=False,
        help_text="Designates whether this user is approved or not.",
    )
    is_staff = models.BooleanField(
        default=True,
        help_text="Designates whether the user can log into this admin site.",
    )
    role = models.ForeignKey(
        Role,
        db_column="RoleId",
        related_name="user_role",
        on_delete=models.CASCADE,
        default=None,
    )
    country = models.ForeignKey(
        Countries,
        db_column="UserCountryId",
        related_name="user_country",
        null=True,
        on_delete=models.CASCADE,
        default=None,
    )
    objects = CustomAccountManager()
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    class Meta:
        db_table = "User"

    def save(self, *args, **kwargs):
        try:
            if not self.pk:
                self.email = self.email.replace(" ", "").lower()
            super().save()
        except Exception:
            raise


class UserInfo(Base):
    user = models.ForeignKey(
        User,
        db_column="UserId",
        related_name="admin_user",
        default=None,
        on_delete=models.CASCADE,
    )
    zone = models.ForeignKey(
        Zone,
        db_column="UserZoneId",
        related_name="user_zone",
        null=True,
        on_delete=models.CASCADE,
        default=None,
    )
    MAIL_NOTIFICATION = (
        (False, "No"),
        (True, "Yes"),
    )
    mail_notification = models.BooleanField(
        db_column="MailNotification", null=True, blank=True, default=False
    )

    class Meta:
        db_table = "UserInfo"


ORDER_COLUMN_CHOICES = Choices(
    ("0", "id"),
    ("1", "name"),
    ("2", "email"),
    ("3", "status"),
)


def query_user_by_args(query_object, **kwargs):
    try:
        draw = int(kwargs.get("draw", None)[0])
        length = int(kwargs.get("length", None)[0])
        start = int(kwargs.get("start", None)[0])
        search_value = kwargs.get("search[value]", None)[0]
        order_column = kwargs.get("order[0][column]", None)[0]
        order = kwargs.get("order[0][dir]", None)[0]
        order_column = ORDER_COLUMN_CHOICES[order_column]

        # django orm '-' -> desc
        if order == "desc":
            order_column = "-" + order_column

        queryset = User.objects.filter(query_object)

        total = queryset.count()
        if search_value:
            queryset = queryset.filter(
                Q(id__icontains=search_value)
                | Q(name__icontains=search_value)
                | Q(email__icontains=search_value)
                | Q(status__icontains=search_value)
            )

        count = queryset.count()
        queryset = queryset.order_by(order_column)[start : start + length]
        return {"items": queryset, "count": count, "total": total, "draw": draw}
    except Exception as e:
        print(e)
        return None


class EmailToken(Base):
    user = models.ForeignKey(
        User,
        db_column="UserId",
        related_name="email_token_user",
        default=None,
        on_delete=models.CASCADE,
    )
    token = models.CharField(
        max_length=255, db_column="Token", null=True, blank=True, default=""
    )

    class Meta:
        db_table = "EmailToken"
