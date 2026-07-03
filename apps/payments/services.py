from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from io import BytesIO
from xhtml2pdf import pisa
from apps.reports.utils import log_audit
from apps.documents.services import create_document
from apps.notifications.services import notify_payment, notify_sale, notify_staff_payment


def process_payment(payment, confirmed_by=None):
    """
    Central payment processing engine.
    Called when a payment is confirmed (manually or via M-Pesa callback).
    """
    with transaction.atomic():
        payment.status = 'confirmed'
        payment.confirmed_by = confirmed_by
        payment.confirmed_at = timezone.now()
        payment.save()

        sale = payment.sale
        amount = payment.amount

        log_audit(
            confirmed_by or payment.customer.user, 'payment',
            model_name='Payment', object_id=payment.pk,
            object_repr=payment.receipt_number,
            description=f'Payment {payment.receipt_number} of KSh {amount:,.0f} confirmed',
        )

        _apply_to_sale(sale, amount)
        _apply_to_installments(sale, amount)
        _check_sale_completion(sale)
        _generate_receipt_document(payment)
        _generate_statement_document(payment)
        _trigger_stage_documents(sale)

        notify_payment(payment.customer.user, amount, payment.receipt_number)
        notify_staff_payment(amount, payment.receipt_number, payment.customer.name)
        if sale.status == 'completed':
            notify_sale(sale.customer.user, sale.plot.plot_number)


def _apply_to_sale(sale, amount):
    if sale.status == 'reservation':
        sale.status = 'active'
    if not sale.deposit_paid and sale.deposit_amount > 0:
        if sale.total_paid >= sale.deposit_amount:
            sale.deposit_paid = True
    sale.save()


def _apply_to_installments(sale, amount):
    pending = sale.schedule.filter(status__in=['pending', 'partially_paid', 'overdue']).order_by('due_date')
    remaining = amount

    for installment in pending:
        if remaining <= 0:
            break
        owed = installment.amount - installment.amount_paid
        if remaining >= owed:
            installment.amount_paid = installment.amount
            remaining -= owed
        else:
            installment.amount_paid += remaining
            remaining = Decimal('0.00')
        installment.update_status()
        installment.save()

    if remaining > 0:
        _apply_advance_payment(sale, remaining)


def _apply_advance_payment(sale, amount):
    future = sale.schedule.filter(status='pending', amount_paid=0).order_by('due_date')
    remaining = amount
    for installment in future:
        if remaining <= 0:
            break
        if remaining >= installment.amount:
            installment.amount_paid = installment.amount
            installment.paid = True
            installment.paid_date = timezone.now().date()
            installment.status = 'paid'
            remaining -= installment.amount
        else:
            installment.amount_paid = remaining
            installment.status = 'partially_paid'
            remaining = Decimal('0.00')
        installment.save()


def _check_sale_completion(sale):
    total_paid = sale.total_paid
    if total_paid >= sale.selling_price:
        sale.status = 'completed'
        sale.completion_date = timezone.now().date()
        sale.save()


def _generate_receipt_document(payment):
    from .models import Payment
    from apps.documents.models import Document
    existing = Document.objects.filter(
        customer=payment.customer,
        sale=payment.sale,
        document_type='payment_receipt',
        title__icontains=payment.receipt_number
    ).exists()
    if existing:
        return
    company = _get_company_settings()
    html = render_to_string('payments/receipt_pdf.html', {
        'payment': payment,
        'company_name': company.get('company_name', 'Prime Lands Ltd'),
        'company_email': company.get('email', 'info@primelands.com'),
        'company_phone': company.get('phone', '+254 700 000 000'),
        'company_address': company.get('address', '99 Westlands Rd, Nairobi'),
        'company_tagline': company.get('tagline', 'Your Trusted Real Estate Partner'),
        'currency': 'KSh',
    })
    pdf_file = _generate_pdf(html)
    if pdf_file:
        from django.core.files.base import ContentFile
        doc = create_document(
            customer=payment.customer,
            doc_type='payment_receipt',
            title=f'Receipt {payment.receipt_number}',
            sale=payment.sale,
            file_content=ContentFile(pdf_file, name=f'{payment.receipt_number}.pdf'),
            is_auto=True,
        )


def _generate_statement_document(payment):
    from apps.documents.models import Document
    statement_data = get_customer_statement(payment.customer, payment.sale)
    company = _get_company_settings()
    html = render_to_string('payments/statement_pdf.html', {
        'statement': statement_data,
        'company_name': company.get('company_name', 'Prime Lands Ltd'),
        'company_tagline': company.get('tagline', 'Your Trusted Real Estate Partner'),
        'company_address': company.get('address', '99 Westlands Rd, Nairobi'),
        'company_phone': company.get('phone', '+254 700 000 000'),
        'company_email': company.get('email', 'info@primelands.com'),
        'currency': 'KSh',
    })
    pdf_file = _generate_pdf(html)
    if pdf_file:
        from django.core.files.base import ContentFile
        from datetime import datetime
        filename = f'statement_{payment.sale.id}_{datetime.now().strftime("%Y%m%d")}.pdf'
        create_document(
            customer=payment.customer,
            doc_type='payment_statement',
            title=f'Payment Statement - {payment.sale.plot.plot_number}',
            sale=payment.sale,
            file_content=ContentFile(pdf_file, name=filename),
            is_auto=True,
        )


def _trigger_stage_documents(sale):
    from apps.documents.services import generate_auto_documents
    generate_auto_documents(sale)


def _get_company_settings():
    try:
        from apps.settings.models import CompanySetting
        setting = CompanySetting.objects.first()
        if setting:
            return {
                'company_name': setting.company_name,
                'email': setting.email,
                'phone': setting.phone,
                'address': setting.address,
                'tagline': setting.tagline,
            }
    except Exception:
        pass
    return {}


def _generate_pdf(html_string):
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode('UTF-8')), result)
    if pdf.err:
        return None
    return result.getvalue()


def get_customer_statement(customer, sale):
    payments = sale.payments.filter(status='confirmed').order_by('payment_date')
    running_balance = sale.selling_price
    lines = []
    for p in payments:
        running_balance -= p.amount
        lines.append({
            'date': p.payment_date,
            'description': f'Payment {p.receipt_number} ({p.get_payment_method_display()})',
            'amount': p.amount,
            'running_balance': running_balance,
        })
    return {
        'customer': customer,
        'sale': sale,
        'plot': sale.plot,
        'selling_price': sale.selling_price,
        'total_paid': sale.total_paid,
        'balance': sale.balance,
        'progress_percent': sale.progress_percent,
        'lines': lines,
        'statement_date': timezone.now(),
    }
