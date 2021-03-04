from authbroker_client.backends import AuthbrokerBackend

from accounts.models import GovDepartment


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
        return GovDepartment.objects.get(email_domains__contains=[domain]).id
    except GovDepartment.DoesNotExist:
        return None


class CustomAuthbrokerBackend(AuthbrokerBackend):
    def get_or_create_user(self, profile):
        if profile["gov_department_id"] is None:
            return None
        return super().get_or_create_user(profile)

    def user_create_mapping(self, profile):
        gov_dep_id = get_gov_department_id_from_user_email(profile["email"])
        return {
            "email": profile["email"],
            "first_name": profile["first_name"],
            "last_name": profile["last_name"],
            "gov_department_id": gov_dep_id,
        }
