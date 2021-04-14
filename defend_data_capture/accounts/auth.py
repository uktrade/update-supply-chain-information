from authbroker_client.backends import AuthbrokerBackend
from django.contrib.auth import get_user_model

from accounts.models import get_gov_department_id_from_user_email

UserModel = get_user_model()


class CustomAuthbrokerBackend(AuthbrokerBackend):
    def get_or_create_user(self, profile):
        id_key = self.get_profile_id_name()
        try:
            return UserModel.objects.get(**{UserModel.USERNAME_FIELD: profile[id_key]})
        except UserModel.DoesNotExist:
            return self.create_user(profile)

    def create_user(self, profile):
        id_key = self.get_profile_id_name()
        user_data = {UserModel.USERNAME_FIELD: profile[id_key]}
        user_mapping = self.user_create_mapping(profile)
        # # if user_mapping["gov_department_id"] is None:
        # #     return None
        user_data.update(user_mapping)
        email = user_data.pop("email")
        user = UserModel.objects.create_user(email, **user_data)
        return user

    def user_create_mapping(self, profile):
        # gov_dep_id = get_gov_department_id_from_user_email(profile["email"])
        return {
            "email": profile["email"],
            "first_name": profile["first_name"],
            "last_name": profile["last_name"],
            # "gov_department_id": gov_dep_id,
        }
