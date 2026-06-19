from django.urls import reverse_lazy
from django.http import Http404

from geo_analytics.models import Field
from geo_analytics.forms import FieldForm
from warehousing.models import Warehouse

from django.views.generic import (
    TemplateView, 
    CreateView,
    UpdateView, 
    DeleteView
)

from django.contrib.auth.mixins import (
    LoginRequiredMixin
)


class MapDashboardView(LoginRequiredMixin, TemplateView):
    """Дашборд з інтерактивною картою."""
    template_name = 'geo_analytics/map_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = Field.objects.filter(company=self.request.user.company)
        context['warehouses'] = Warehouse.objects.filter(company=self.request.user.company)
        return context


class FieldCreateView(LoginRequiredMixin, CreateView):
    """Сторінка створення нового поля."""

    model = Field
    form_class = FieldForm
    template_name = 'geo_analytics/field_editor.html'
    success_url = reverse_lazy('map_dashboard')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.company = self.request.user.company
        return super().form_valid(form)


class FieldUpdateView(LoginRequiredMixin, UpdateView):
    """Сторінка редагування поля."""
    
    model = Field
    form_class = FieldForm
    template_name = 'geo_analytics/field_editor.html'
    success_url = reverse_lazy('map_dashboard')


class FieldDeleteView(LoginRequiredMixin, DeleteView):
    """Сторінка підтвердження видалення поля."""

    model = Field
    template_name = 'geo_analytics/field_confirm_delete.html'
    success_url = reverse_lazy('map_dashboard')

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return queryset.filter(company=self.request.user.company)
        
        raise Http404("Ви не маєте доступу до цього об'єкта або не авторизовані.")
