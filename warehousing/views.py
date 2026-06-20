from django.urls import reverse_lazy
from django.http import Http404

from .models import (
    Warehouse, 
    WarehouseJournalEntry
)

from .forms import (
    GrainOutgoingForm, 
    GrainIncomingForm, 
    WarehouseForm
)

from django.views.generic import (
    CreateView, 
    ListView, 
    DeleteView,
    FormView
)

from django.contrib.auth.mixins import (
    LoginRequiredMixin, 
    PermissionRequiredMixin
)


class WarehouseListView(LoginRequiredMixin, ListView):
    """Список складів компанії з показниками завантаженості."""

    model = Warehouse
    template_name = 'warehousing/warehouse_list.html'
    context_object_name = 'warehouses'

    def get_queryset(self):
        return Warehouse.objects.filter(
            company=self.request.user.company
        )


class WarehouseCreateView(PermissionRequiredMixin, CreateView):
    """Сторінка додавання нового складу на карту."""

    model = Warehouse
    form_class = WarehouseForm
    template_name = 'warehousing/warehouse_form.html'
    success_url = reverse_lazy('warehouse_list')
    permission_required = 'warehousing.add_warehouse'

    def form_valid(self, form):
        """Прив'язує новий склад до компанії користувача."""

        form.instance.company = self.request.user.company
        return super().form_valid(form)


class WarehouseDeleteView(PermissionRequiredMixin, DeleteView):
    """Сторінка підтвердження видалення складу."""

    model = Warehouse
    template_name = 'warehousing/warehouse_confirm_delete.html'
    success_url = reverse_lazy('warehouse_list')
    permission_required = 'warehousing.delete_warehouse'

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.user.is_authenticated and hasattr(self.request.user, 'company'):
            return queryset.filter(company=self.request.user.company)
        
        raise Http404("Доступ заборонено.")


class InventoryJournalView(LoginRequiredMixin, ListView):
    """Журнал складських операцій для всіх складів компанії."""

    model = WarehouseJournalEntry
    template_name = 'warehousing/journal.html'
    context_object_name = 'entries'

    def get_queryset(self):
        return WarehouseJournalEntry.objects.filter(
            warehouse__company=self.request.user.company
        )


class GrainIncomingCreateView(LoginRequiredMixin, FormView):
    "Сторінка для створення нової патії і запису транзакції"
    
    template_name = 'warehousing/incoming_form.html'
    form_class = GrainIncomingForm
    success_url = reverse_lazy('warehouses_journal')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        form.save(operator=self.request.user)
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        warehouse_id = self.request.GET.get('warehouse_id')
        if warehouse_id:
            initial['warehouse'] = warehouse_id
        return initial
    
    
class GrainOutgoingCreateView(LoginRequiredMixin, FormView):
    "Сторінка для операцій списання та бронювання існуючих партій "

    template_name = 'warehousing/outgoing_form.html'
    form_class = GrainOutgoingForm
    success_url = reverse_lazy('warehouses_journal')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = self.request.user.company
        return kwargs

    def form_valid(self, form):
        form.save(operator=self.request.user)
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        warehouse_id = self.request.GET.get('warehouse_id')
        if warehouse_id:
            initial['warehouse'] = warehouse_id
        return initial