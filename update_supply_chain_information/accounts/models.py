import uuid

from django.db import models
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField


def get_gov_department_id_from_user_email(email):
    """
    A function that takes in an email, obtains the domain and queries the database for a
    government department with a matching domain listed under it's email_domains field. If successful
    it returns the department, otherwise it returns None.
    """
    domain = email.split("@", 1)[1]
    # A government department needs to be added to the db before new
    # users from that department can access the app
    try:
        return GovDepartment.objects.get(email_domains__contains=[domain])
    except GovDepartment.DoesNotExist:
        return None


class UserManager(BaseUserManager):
    def create_user(self, email, **kwargs):
        email = self.normalize_email(email)
        # Ensure the government department is set
        gov_department = kwargs.get("gov_department", None)
        if gov_department is None:
            gov_department = get_gov_department_id_from_user_email(email)
            if gov_department is None:
                return None
            kwargs["gov_department"] = gov_department
        user = self.model(email=email, **kwargs)
        # no password passed in => don't allow password authentication
        password = kwargs.get("password", None)
        if password is None:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
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
    is_staff = models.BooleanField(
        "Staff",
        default=False,
        help_text="Indicates whether the user can log in to the admin site.",
    )
    is_active = models.BooleanField(
        "Active",
        default=True,
        help_text="Designates whether this user should be treated as active. "
        "Unselect this instead of deleting accounts.",
    )
    USERNAME_FIELD = "sso_email_user_id"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class GovDepartment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH)
    email_domains = ArrayField(models.CharField(max_length=100))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.email_domains = [domain.lower() for domain in self.email_domains]
        super(GovDepartment, self).save(*args, **kwargs)
