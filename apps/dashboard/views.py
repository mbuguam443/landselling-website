from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.sales.models import Sale
from apps.payments.models import Payment
from apps.customers.models import Customer
from apps.plots.models import Plot
from apps.notifications.models import Notification
from apps.sales.utils import get_overdue_summary
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, datetime
import json


def get_admin_dashboard_context():
    """Shared context for the admin analytics dashboard."""
    now = timezone.now()

    months = []
    monthly_revenue_data = []
    monthly_sales_data = []
    for i in range(5, -1, -1):
        first = now.replace(day=1) - timedelta(days=30 * i)
        month_start = first.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            month_end = month_start.replace(day=1) + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(seconds=1)
        else:
            month_end = now
        label = month_start.strftime('%b %Y')
        months.append(label)
        rev = Payment.objects.filter(
            status='confirmed',
            payment_date__gte=month_start.date(),
            payment_date__lte=month_end.date(),
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_revenue_data.append(float(rev))
        sales_count = Sale.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end,
        ).count()
        monthly_sales_data.append(sales_count)

    monthly_payments = []
    for i in range(5, -1, -1):
        first = now.replace(day=1) - timedelta(days=30 * i)
        month_start = first.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            month_end = month_start.replace(day=1) + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(seconds=1)
        else:
            month_end = now
        total = Payment.objects.filter(
            status='confirmed',
            created_at__gte=month_start,
            created_at__lte=month_end,
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_payments.append(float(total))

    plot_statuses = ['available', 'reserved', 'sold', 'blocked']
    plot_status_counts = []
    plot_status_labels = []
    for s in plot_statuses:
        count = Plot.objects.filter(status=s).count()
        if count > 0:
            plot_status_labels.append(dict(Plot.STATUS_CHOICES)[s])
            plot_status_counts.append(count)

    from apps.sales.utils import check_overdue_installments
    check_overdue_installments()

    from apps.subscriptions.models import SubscriptionPayment, Subscription
    total_revenue = Payment.objects.filter(status='confirmed').aggregate(
        total=Sum('amount'))['total'] or 0
    total_commission = Sale.objects.filter(commission_paid=True).aggregate(
        total=Sum('commission_amount'))['total'] or 0
    total_subscription = SubscriptionPayment.objects.filter(status='confirmed').aggregate(
        total=Sum('amount'))['total'] or 0

    ctx = {
        'total_customers': Customer.objects.count(),
        'total_plots': Plot.objects.count(),
        'available_plots': Plot.objects.filter(status='available').count(),
        'sold_plots': Plot.objects.filter(status='sold').count(),
        'reserved_plots': Plot.objects.filter(status='reserved').count(),
        'total_revenue': total_revenue,
        'total_commission': total_commission,
        'total_subscription': total_subscription,
        'active_sales': Sale.objects.filter(status='active').count(),
        'active_subscriptions': Subscription.objects.filter(is_active=True, end_date__gte=timezone.now().date()).count(),
        'recent_sales': Sale.objects.select_related('customer__user', 'plot__project').order_by('-created_at')[:5],
        'recent_payments': Payment.objects.select_related('customer__user').filter(
            status='confirmed').order_by('-created_at')[:5],
        'chart_months': json.dumps(months),
        'chart_monthly_revenue': json.dumps(monthly_revenue_data),
        'chart_monthly_sales': json.dumps(monthly_sales_data),
        'chart_monthly_payments': json.dumps(monthly_payments),
        'chart_plot_labels': json.dumps(plot_status_labels),
        'chart_plot_counts': json.dumps(plot_status_counts),
    }

    month_ago = now - timedelta(days=30)
    monthly = Payment.objects.filter(status='confirmed', created_at__gte=month_ago).aggregate(
        total=Sum('amount'))['total'] or 0
    ctx['monthly_collections'] = monthly
    ctx['overdue_summary'] = get_overdue_summary()

    agent_revenue = (
        Payment.objects.filter(status='confirmed', sale__sales_agent__isnull=False)
        .values(
            'sale__sales_agent__id',
            'sale__sales_agent__username',
            'sale__sales_agent__first_name',
            'sale__sales_agent__last_name',
        )
        .annotate(total=Sum('amount'), sale_count=Count('id'))
        .order_by('-total')
    )
    for a in agent_revenue:
        name = f"{a['sale__sales_agent__first_name']} {a['sale__sales_agent__last_name']}".strip()
        a['display_name'] = name if name else a['sale__sales_agent__username']
    ctx['agent_revenue'] = agent_revenue
    ctx['total_agent_revenue'] = sum(a['total'] for a in agent_revenue)

    return ctx


@login_required
def home(request):
    user = request.user

    if user.is_staff_or_above() or user.is_superuser:
        # Super admin / administrator → revenue report
        if user.role in ('super_admin', 'administrator'):
            return redirect('reports:revenue_report')

        # Other staff → analytics dashboard
        context = get_admin_dashboard_context()
        return render(request, 'dashboard/admin_dashboard.html', context)

    # Customer dashboard
    customer = Customer.objects.filter(user=user).first()
    sales_qs = Sale.objects.filter(customer=customer).order_by('-created_at') if customer else Sale.objects.none()
    payments_qs = Payment.objects.filter(customer=customer).order_by('-created_at') if customer else Payment.objects.none()
    total_paid = payments_qs.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0
    remaining_balance = 0
    active_sale = sales_qs.filter(status='active').first()
    if active_sale:
        remaining_balance = active_sale.selling_price - total_paid
        if remaining_balance < 0:
            remaining_balance = 0
    sales = list(sales_qs[:5])
    payments = list(payments_qs[:5])
    notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:5]
    return render(request, 'dashboard/customer_dashboard.html', {
        'customer': customer,
        'sales': sales,
        'payments': payments,
        'notifications': notifications,
        'total_paid': total_paid,
        'remaining_balance': remaining_balance,
    })
