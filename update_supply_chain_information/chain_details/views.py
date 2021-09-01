from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView


class ChainDetailsView(LoginRequiredMixin, TemplateView):
    template_name = "chain_details_base.html"
