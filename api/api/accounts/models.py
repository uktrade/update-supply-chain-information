from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
import uuid


class UserManager(BaseUserManager):
    def create_user(self):
        pass

    def create_superuser(self):
        pass


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sso_email_user_id = models.EmailField(
        unique=True,
        max_length=254,  # The length of the field in Staff SSO is 254 characters.
        verbose_name="SSO email user ID",
        help_text="This is the `Email user ID` that is shown for this user in Staff SSO.",
    )
    first_name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH)
    last_name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH)
    email = models.EmailField()
    gov_department = models.ForeignKey(
        "GovDepartment",
        on_delete=models.PROTECT,
        related_name="users",
    )
    USERNAME_FIELD = "sso_email_user_id"


class GovDepartment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH)
