from django.shortcuts import redirect
from django.views.generic import FormView
from django.http import HttpResponse
from django.urls import reverse

from action_progress.forms import SAPForm
from supply_chains.models import SupplyChain


class ActionProgressView(FormView):
    template_name = "action_progress_base.html"
    form_class = SAPForm

    def get_initial(self):
        print("++++++ GET INIT +++++++++")
        form_value = self.initial.copy()
        dept = self.request.GET.get("dept", None)
        form_value["department"] = dept

        return form_value

    def get_form_kwargs(self):
        print("++++++ GET KWARGS +++++++++")
        kwargs = super().get_form_kwargs()

        dept = kwargs["initial"]["department"]
        if dept:
            kwargs["supply_chain_qs"] = SupplyChain.objects.filter(
                gov_department__id=dept
            )

        return kwargs

    def get_success_url(self) -> str:
        print("++++++ GET SUCCESS URL +++++++++")
        return HttpResponse(status=204)
        # form = self.get_form()
        # valid = form.is_valid()
        # print(valid)
        # return reverse(
        #     "action-progress-dept", kwargs={"dept": form.cleaned_data["department"]}
        # )

    def post(self, request):
        print("++++++ POST +++++++++")
        dept = request.POST.get("department", None)
        print(f"DEPT: {dept}")

        form = self.get_form()
        validity = form.is_valid()
        print(f"Form: {validity}")

        if form.is_valid():
            # return self.form_valid(form)
            return HttpResponse(status=204)
        elif dept:
            url = reverse("action-progress") + f"?dept={dept}"
            return redirect(url)
        else:
            return self.form_invalid(form)
