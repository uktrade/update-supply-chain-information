from django.core.management.base import BaseCommand, CommandError

from config.settings.settings import env
from accounts.models import User

user_name = env("LOCAL_USER_FIRST_NAME")


class Command(BaseCommand):
    help = "Make local user as admin(for dev purpose only!)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--first_name",
            help="First name of the user to elevate as admin",  # /PS-IGNORE
        )

    def handle(self, **options):
        if not (options.get("first_name", None) or user_name):
            raise CommandError("No user specified")
        else:
            first_name = options.get("first_name", None) or user_name

        user_object = User.objects.get(first_name=first_name)

        user_object.is_staff = user_object.is_superuser = True
        user_object.save()

        self.stdout.write(self.style.SUCCESS(f"{first_name} now is admin!"))
