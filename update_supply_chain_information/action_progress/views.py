from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class ActionProgressView(TemplateView):
    template_name = "action_progress_base.html"
