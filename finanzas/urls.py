from django.urls import path
from .views import TransactionListView, TransactionCreateView, report_view

urlpatterns = [
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions/add/', TransactionCreateView.as_view(), name='transaction_add'),
    path('reports/', report_view, name='reports'),
]