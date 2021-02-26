from authbroker_client.backends import AuthbrokerBackend

from accounts.models import GovDepartment


def get_gov_department_id_from_user_email(email):
    domain = email.split("@", 1)[1]
    # A government department needs to be added to the db before new
    # users from that department can access the app
    gov_department = GovDepartment.objects.get(email_domains__contains=[domain])
    return gov_department.id


class CustomAuthbrokerBackend(AuthbrokerBackend):
    def user_create_mapping(self, profile):
        gov_dep_id = get_gov_department_id_from_user_email(profile["email"])

        return {
            "email": profile["email"],
            "first_name": profile["first_name"],
            "last_name": profile["last_name"],
            "gov_department_id": gov_dep_id,
        }
