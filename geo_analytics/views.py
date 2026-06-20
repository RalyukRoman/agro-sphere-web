from django.urls import reverse_lazy
from django.http import Http404
import json

from .models import Field
from .forms import FieldForm
from warehousing.models import Warehouse

from django.views.generic import (
    TemplateView, 
    CreateView,
    UpdateView, 
    DeleteView
)

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin
)


class MapDashboardView(LoginRequiredMixin, TemplateView):
    """Дашборд з інтерактивною картою."""
    template_name = 'geo_analytics/map_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = Field.objects.filter(company=self.request.user.company)
        
        fields_list = []
        for field in fields:
            if field.geom:
                fields_list.append({
                    "id": str(field.pk),
                    "name": field.name,
                    "area": str(field.area_hectares or 0),
                    "status": field.get_crop_status_display(),
                    "geom": json.loads(field.geom.json),
                    "editUrl": str(reverse_lazy('field_edit', args=[field.pk])),
                    "deleteUrl": str(reverse_lazy('field_delete', args=[field.pk]))
                })
        
        context['fields_json'] = fields_list
        context['warehouses'] = Warehouse.objects.filter(company=self.request.user.company)
        return context


class FieldCreateView(PermissionRequiredMixin, CreateView):
    """Сторінка створення нового поля."""

    model = Field
    form_class = FieldForm
    template_name = 'geo_analytics/field_editor.html'
    success_url = reverse_lazy('map_dashboard')
    permission_required = 'geo_analytics.add_field'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.company = self.request.user.company
        return super().form_valid(form)


class FieldUpdateView(PermissionRequiredMixin, UpdateView):
    """Сторінка редагування поля."""
    
    model = Field
    form_class = FieldForm
    template_name = 'geo_analytics/field_editor.html'
    success_url = reverse_lazy('map_dashboard')
    permission_required = 'geo_analytics.change_field'


class FieldDeleteView(PermissionRequiredMixin, DeleteView):
    """Сторінка підтвердження видалення поля."""

    model = Field
    template_name = 'geo_analytics/field_confirm_delete.html'
    success_url = reverse_lazy('map_dashboard')
    permission_required = 'geo_analytics.delete_field'

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return queryset.filter(company=self.request.user.company)
        
        raise Http404("Ви не маєте доступу до цього об'єкта або не авторизовані.")
