from authbroker_client.backends import AuthbrokerBackend
from django.contrib.auth import get_user_model

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
        user_data.update(user_mapping)
        email = user_data.pop("email")
        user = UserModel.objects.create_user(email, **user_data)
        return user
