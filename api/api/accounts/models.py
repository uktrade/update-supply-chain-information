from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
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


def _check_email_domains_unique(email_domains):
    for email in email_domains:
        if GovDepartment.objects.filter(email_domains__contains=[email]):
            raise ValidationError(
                f"The domain '{email}' already exists for another government department.",
            )


class GovDepartment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH)
    email_domains = ArrayField(models.CharField(max_length=100))

    def __str__(self):
        return self.name

    def clean_fields(self, exclude=None):
        super().clean_fields(exclude=exclude)
        self.email_domains = [domain.lower() for domain in self.email_domains]
        _check_email_domains_unique(self.email_domains)

    def save(self, *args, **kwargs):
        self.clean_fields()
        super(GovDepartment, self).save(*args, **kwargs)
