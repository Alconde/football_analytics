from django.shortcuts import render
import uuid
from django.db.models import Avg
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from apps.core.staff_role_mixins import RoleRequiredMixin
from apps.users.models import User

from .forms import GeneratedReportForm
from .models import GeneratedReport
from .tasks import generate_report_async


class GeneratedReportListView(RoleRequiredMixin, ListView):
    allowed_roles = ()
    model = GeneratedReport
    template_name = "reports/report_list.html"
    context_object_name = "reports"
    paginate_by = 20


class GeneratedReportCreateView(RoleRequiredMixin, CreateView):
    allowed_roles = (
        User.Role.ADMIN,
        User.Role.TACTICAL_ANALYST,
        User.Role.DATA_ANALYST,
    )
    model = GeneratedReport
    form_class = GeneratedReportForm
    template_name = "reports/report_form.html"
    success_url = reverse_lazy("reports:list")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.generated_by = self.request.user

        placeholder = ContentFile(
            "Generando informe de análisis.".encode("utf-8"),
            name=f"pending-{uuid.uuid4().hex[:8]}.{self.object.file_type}",
        )
        self.object.file.save(placeholder.name, placeholder, save=False)
        self.object.save()

        generate_report_async.delay(self.object.pk)
        return HttpResponseRedirect(self.get_success_url())
