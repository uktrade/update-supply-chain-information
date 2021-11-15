from django.contrib.auth.mixins import UserPassesTestMixin


class DeptAuthRequiredMixin(UserPassesTestMixin):
    """Mixin to validate departmental authorisation.

    This mixin inherits from UserPassesTestMixin to define test_func where
    departmental auth will be checked. It returns True when user is either
    an admin or has access to the department.

    This mixin expects attribute 'dept' to be initialised with name of the department
    from inherited class

    Note: As UserPassesTestMixin has been used here which over-rides
    LoginRequiredMixin(by the looks of it). Hence condition also include user login.
    """

    def test_func(self):
        claimed_dept = self.kwargs.get("dept", None)
        return self.request.user.is_authenticated and (
            self.request.user.is_admin
            or self.request.user.gov_department.name == claimed_dept
        )
