from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse

from chain_details.forms import SCDForm


class ChainDetailsView(LoginRequiredMixin, FormView):
    template_name = "chain_details_base.html"
    form_class = SCDForm

    def get_success_url(self):

        form = self.get_form()
        form.is_valid()

        return reverse(
            "chain-details-list",
            kwargs={
                "dept": form.cleaned_data["department"],
            },
        )


class ChainDetailsListView(ChainDetailsView):
    template_name = "chain_details_list.html"
