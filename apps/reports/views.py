from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import models
from django.template.loader import render_to_string
from apps.accounts.decorators import staff_required
from apps.sales.models import Sale
from apps.payments.models import Payment
from apps.customers.models import Customer
from apps.plots.models import Plot
import csv
import openpyxl
from xhtml2pdf import pisa


@login_required
@staff_required
def report_dashboard(request):
    return render(request, 'reports/report_dashboard.html')


@login_required
@staff_required
def sales_report(request):
    from apps.dashboard.views import get_admin_dashboard_context
    context = get_admin_dashboard_context()
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@staff_required
def payments_report(request):
    from apps.core.utils import get_sortable_context
    payments = Payment.objects.select_related('sale__plot', 'customer__user', 'confirmed_by').all()
    ctx = get_sortable_context(request, payments, default_sort='-payment_date',
                               allowed_fields=['receipt_number', 'customer__name', 'amount', 'status', 'payment_date'],
                               search_fields=['receipt_number', 'customer__name', 'status'],
                               per_page=15)
    return render(request, 'reports/payments_report.html', ctx)


@login_required
@staff_required
def revenue_report(request):
    from apps.payments.models import Payment
    from apps.subscriptions.models import SubscriptionPayment
    total_revenue = Payment.objects.filter(status='confirmed').aggregate(
        total=models.Sum('amount'))['total'] or 0
    total_commission = Sale.objects.filter(commission_paid=True).aggregate(
        total=models.Sum('commission_amount'))['total'] or 0
    total_subscription = SubscriptionPayment.objects.filter(status='confirmed').aggregate(
        total=models.Sum('amount'))['total'] or 0
    commission_sales = Sale.objects.filter(commission_amount__gt=0).select_related('customer', 'plot')[:20]
    sub_payments = SubscriptionPayment.objects.filter(status='confirmed').select_related('user')[:20]
    return render(request, 'reports/revenue_report.html', {
        'total_revenue': total_revenue,
        'total_commission': total_commission,
        'total_subscription': total_subscription,
        'commission_sales': commission_sales,
        'sub_payments': sub_payments,
    })


@login_required
@staff_required
def customers_report(request):
    from apps.core.utils import get_sortable_context
    customers = Customer.objects.select_related('user').all()
    ctx = get_sortable_context(request, customers, default_sort='-created_at',
                               allowed_fields=['name', 'email', 'phone', 'city', 'created_at'],
                               search_fields=['name', 'email', 'phone', 'city'],
                               per_page=15)
    return render(request, 'reports/customers_report.html', ctx)


@login_required
@staff_required
def analytics_dashboard(request):
    from apps.dashboard.views import get_admin_dashboard_context
    context = get_admin_dashboard_context()
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
@staff_required
def export_report(request, report_type, format):
    from django.db import models
    response = HttpResponse(content_type='text/csv')

    if format == 'csv':
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'
        writer = csv.writer(response)

        if report_type == 'sales':
            writer.writerow(['Customer', 'Plot', 'Price', 'Status', 'Date'])
            for s in Sale.objects.select_related('customer__user', 'plot__project').all():
                writer.writerow([s.customer.name, str(s.plot), s.selling_price, s.status, s.sale_date])

        elif report_type == 'payments':
            writer.writerow(['Receipt', 'Customer', 'Amount', 'Method', 'Status', 'Date'])
            for p in Payment.objects.select_related('customer__user').all():
                writer.writerow([p.receipt_number, p.customer.name, p.amount, p.payment_method, p.status, p.payment_date])

        elif report_type == 'customers':
            writer.writerow(['Name', 'Email', 'Phone', 'City', 'Date Joined'])
            for c in Customer.objects.select_related('user').all():
                writer.writerow([c.name, c.email, c.phone, c.city, c.created_at])

    elif format == 'xlsx':
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = report_type.capitalize()

        if report_type == 'sales':
            ws.append(['Customer', 'Plot', 'Price', 'Status', 'Date'])
            for s in Sale.objects.select_related('customer__user', 'plot__project').all():
                ws.append([s.customer.name, str(s.plot), float(s.selling_price), s.status, str(s.sale_date)])

        elif report_type == 'payments':
            ws.append(['Receipt', 'Customer', 'Amount', 'Method', 'Status', 'Date'])
            for p in Payment.objects.select_related('customer__user').all():
                ws.append([p.receipt_number, p.customer.name, float(p.amount), p.payment_method, p.status, str(p.payment_date)])

        elif report_type == 'customers':
            ws.append(['Name', 'Email', 'Phone', 'City', 'Date Joined'])
            for c in Customer.objects.select_related('user').all():
                ws.append([c.name, c.email, c.phone, c.city, str(c.created_at)])

        wb.save(response)

    elif format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'

        template_data = {'report_type': report_type, 'report_date': __import__('datetime').datetime.now()}

        if report_type == 'sales':
            template_data['sales'] = Sale.objects.select_related('customer__user', 'plot__project').all()
        elif report_type == 'payments':
            template_data['payments'] = Payment.objects.select_related('customer__user').all()
        elif report_type == 'customers':
            template_data['customers'] = Customer.objects.select_related('user').all()
        elif report_type == 'plots':
            template_data['plots'] = Plot.objects.select_related('project').all()

        html = render_to_string('reports/pdf_report.html', template_data)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('PDF generation error', status=500)

    return response
