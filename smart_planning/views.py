from django.urls import reverse_lazy
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from .forms import (
    SmartPlanningCalculateForm,
    CropCultureForm
)

from .models import CropPlan, CropCulture
from .services import CropSolverService
import json

from django.views.generic import (
    TemplateView, 
    FormView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)

from django.contrib.auth.mixins import (
    LoginRequiredMixin, 
    PermissionRequiredMixin
)


class CropCultureListView(LoginRequiredMixin, ListView):
    """Відображення списку всіх доступних культур."""

    model = CropCulture
    template_name = 'smart_planning/culture_list.html'
    context_object_name = 'cultures'
    ordering = ['name']


class CropCultureCreateView(PermissionRequiredMixin, CreateView):
    """Створення нової культури."""

    model = CropCulture
    form_class = CropCultureForm
    template_name = 'smart_planning/culture_form.html'
    success_url = reverse_lazy('culture_list')
    permission_required = 'smart_planning.add_cropculture'

    def form_valid(self, form):
        return super().form_valid(form)


class CropCultureUpdateView(PermissionRequiredMixin, UpdateView):
    """Редагування існуючої культури."""

    model = CropCulture
    form_class = CropCultureForm
    template_name = 'smart_planning/culture_form.html'
    success_url = reverse_lazy('culture_list')
    permission_required = 'smart_planning.change_cropculture'

    def form_valid(self, form):
        return super().form_valid(form)


class CropCultureDeleteView(PermissionRequiredMixin, DeleteView):
    """Видалення культури з системи."""

    model = CropCulture
    template_name = 'smart_planning/culture_confirm_delete.html'
    success_url = reverse_lazy('culture_list')
    permission_required = 'smart_planning.delete_cropculture'

    def delete(self, request, *args, **kwargs):
        return super().delete(
            request, *args, **kwargs
        )


class PlanCalculatorView(LoginRequiredMixin, FormView):
    """Форма для розрахунку оптимального плану посіву."""
    
    form_class = SmartPlanningCalculateForm
    template_name = 'smart_planning/calculator.html'
    
    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs
    
    def form_valid(self, form):
        field = form.cleaned_data['field']
        budget = form.cleaned_data['budget']
        
        result = CropSolverService.calculate_optimal_plan(
            field_id=str(field.id), 
            budget=budget
        )
        
        if "error" in result:
            form.add_error(None, result["error"])
            return self.form_invalid(form)
            
        return redirect(
            f"{reverse_lazy('plan_results')}?plan_id={result['plan_id']}"
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_crops'] = CropCulture.objects.exists() 
        return context


class PlanResultsView(LoginRequiredMixin, TemplateView):
    """Сторінка результатів розрахунку з динамічними даними."""

    template_name = 'smart_planning/results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan_id = self.request.GET.get('plan_id')

        if not plan_id:
            raise Http404(
                "Параметр plan_id відсутній. " \
                "Будь ласка, виконайте розрахунок спочатку."
            )

        crop_plan = get_object_or_404(
            CropPlan.objects.select_related('field', 'suggested_crop'), 
            id=plan_id, 
            field__company=self.request.user.company
        )
        
        chart_labels = [crop_plan.suggested_crop.name]
        chart_data = [float(crop_plan.field.area_hectares)]
        
        total_revenue = float(crop_plan.estimated_profit) / 0.7
        calculated_costs = total_revenue * 0.30

        table_rows = [{
            'field': crop_plan.field.name,
            'crop': crop_plan.suggested_crop.name,
            'area': float(crop_plan.field.area_hectares),
            'yield': float(crop_plan.expected_yield),
            'costs': round(calculated_costs, 2)
        }]

        efficiency_rate = (
            int(crop_plan.confidence_score * 100) 
            if crop_plan.confidence_score else 100
        )

        context['plan'] = {
            'total_profit': float(crop_plan.estimated_profit),
            'efficiency_rate': efficiency_rate,
            'recommended_crop': crop_plan.suggested_crop.name,
            'table_rows': table_rows
        }
        
        context['chart_labels_json'] = json.dumps(chart_labels)
        context['chart_data_json'] = json.dumps(chart_data)
        
        return context