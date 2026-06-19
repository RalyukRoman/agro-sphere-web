from django.urls import path

from .views import (
    WarehouseListView, 
    WarehouseCreateView, 
    WarehouseDeleteView,
    InventoryJournalView, 
    GrainIncomingCreateView,
    GrainOutgoingCreateView
)


urlpatterns = [
    path('warehouses/', WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouses/add/', WarehouseCreateView.as_view(), name='warehouse_add'),
    path('warehouses/<uuid:pk>/delete/', WarehouseDeleteView.as_view(), name='warehouse_delete'),
    path('warehouses/journal/', InventoryJournalView.as_view(), name='inventory_journal'),
    path('warehouse/incoming/', GrainIncomingCreateView.as_view(), name='grain_incoming'),
    path('warehouse/outgoing/', GrainOutgoingCreateView.as_view(), name='grain_outgoing')
]
