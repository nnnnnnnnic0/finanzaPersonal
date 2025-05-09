import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import Transaction
from .forms import TransactionForm
from django.db.models import Sum
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncDay
from django.shortcuts import render

def home_view(request):
    return render(request, 'finanzas/home.html')


class TransactionListView(ListView):
    model = Transaction
    template_name = 'finanzas/transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)  # Si usas autenticación

class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finanzas/transaction_form.html'
    success_url = '/transactions/'

    def form_valid(self, form):
        form.instance.user = self.request.user  # Asigna el usuario autenticado
        return super().form_valid(form)
    

@login_required
def report_view(request):
    user = request.user
    # Tendencias DIARIAS (últimos 30 días)
    today = timezone.now().date()
    start_date = today - timezone.timedelta(days=30)

    daily_trends = list(
        Transaction.objects.filter(user=user, fecha__gte=start_date)
        .annotate(day=TruncDay('fecha'))  # Agrupa por día
        .values('day', 'categoria__type')
        .annotate(total=Sum('costo'))
        .order_by('day')
    )

    # Formatea las fechas y convierte total a float
    for item in daily_trends:
        item['day'] = item['day'].strftime('%Y-%m-%d')
        item['total'] = float(item['total'])
    
    transactions = Transaction.objects.filter(
        user=user,
        fecha__month=today.month,
        fecha__year=today.year
    )
    
    # Convertir a float y formatear
    total_income = float(transactions.filter(categoria__type='income').aggregate(Sum('costo'))['costo__sum']) or 0.0
    total_expense = float(transactions.filter(categoria__type='expense').aggregate(Sum('costo'))['costo__sum']) or 0.0
    balance = total_income - abs(total_expense)  
    
    # Distribución de gastos (convertir total a float)
    expense_categories = list(
        transactions.filter(categoria__type='expense')
        .values('categoria__name')
        .annotate(total=Sum('costo'))
    )
    for item in expense_categories:
        item['total'] = float(item['total'])  # ← Conversión clave
    
    # En la sección de monthly_trends:
    monthly_trends = list(
        Transaction.objects.filter(user=user)
        .annotate(month=TruncMonth('fecha'))
        .values('month', 'categoria__type')
        .annotate(total=Sum('costo'))
        .order_by('month')
    )

    # Formatear mes como 'YYYY-MM'
    for item in monthly_trends:
        item['month'] = item['month'].strftime('%Y-%m')
        item['total'] = float(item['total'])
    
    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'expense_categories': expense_categories,
        'monthly_trends': monthly_trends,
        'daily_trends_json': daily_trends,
    }

    return render(request, 'finanzas/reports.html', context)