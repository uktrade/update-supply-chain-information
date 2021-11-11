import time

from django.views.generic import TemplateView

from healthcheck.checks import db_check
from healthcheck.constants import HealthStatus


class HealthCheckView(TemplateView):
    template_name = "healthcheck.xml"

    def get_context_data(self, **kwargs):
        """Adds status and response time to response context."""
        context = super().get_context_data(**kwargs)
        context["status"] = db_check()
        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time
        return context

    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        if context["status"] == HealthStatus.OK:
            status = 200
        else:
            status = 503
        response = self.render_to_response(context, status=status)
        response["Content-Type"] = "text/xml"
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
