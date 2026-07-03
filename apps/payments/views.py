from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import staff_required
from apps.reports.utils import log_audit
from .models import Payment
from .forms import PaymentForm


@login_required
def payment_list(request):
    from apps.core.utils import get_sortable_context
    if request.user.is_staff_or_above() or request.user.is_superuser:
        payments_list = Payment.objects.select_related('sale__plot', 'customer__user', 'confirmed_by').all()
        template = 'payments/payment_list.html'
    else:
        payments_list = Payment.objects.filter(customer__user=request.user).select_related('sale__plot', 'confirmed_by')
        template = 'payments/customer_payment_list.html'
    ctx = get_sortable_context(request, payments_list, default_sort='-payment_date',
                               allowed_fields=['receipt_number', 'amount', 'status', 'payment_date', 'payment_method'],
                               search_fields=['receipt_number', 'customer__name', 'payment_method', 'status'],
                               per_page=15)
    ctx['is_staff'] = request.user.is_staff_or_above() or request.user.is_superuser
    return render(request, template, ctx)


@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related('sale__plot__project', 'customer__user', 'confirmed_by'),
        pk=pk
    )
    if not (request.user.is_staff_or_above() or request.user.is_superuser) and payment.customer.user != request.user:
        messages.error(request, 'You do not have access to this payment.')
        return redirect('dashboard:home')
    template = 'payments/payment_detail.html' if request.user.is_staff_or_above() or request.user.is_superuser else 'payments/customer_payment_detail.html'
    return render(request, template, {'payment': payment, 'is_staff': request.user.is_staff_or_above() or request.user.is_superuser})


@login_required
@staff_required
def payment_create(request):
    form = PaymentForm()
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.status = 'pending'
            payment.save()
            log_audit(request.user, 'payment', model_name='Payment', object_id=payment.pk,
                      object_repr=payment.receipt_number, description=f'Payment of {payment.amount} recorded', request=request)
            messages.success(request, 'Payment recorded successfully.')
            return redirect('payments:payment_detail', pk=payment.pk)
    return render(request, 'payments/payment_form.html', {'form': form, 'title': 'Record Payment'})


@login_required
@staff_required
def payment_confirm(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        from .services import process_payment
        process_payment(payment, confirmed_by=request.user)
        messages.success(request, f'Payment {payment.receipt_number} confirmed.')
        return redirect('payments:payment_detail', pk=payment.pk)
    return render(request, 'payments/payment_confirm.html', {'payment': payment})


@login_required
def payment_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if not (request.user.is_staff_or_above() or request.user.is_superuser) and payment.customer.user != request.user:
        messages.error(request, 'You do not have access to this receipt.')
        return redirect('dashboard:home')
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa
    import io

    from apps.settings.models import CompanySetting
    cs = CompanySetting.objects.first()
    html = render_to_string('payments/receipt_pdf.html', {
        'payment': payment,
        'company_name': cs.company_name if cs else 'Prime Lands Ltd',
        'company_email': cs.email if cs else 'info@primelands.com',
        'company_phone': cs.phone if cs else '0728627678',
        'company_address': cs.address if cs else '99 Westlands Rd, Nairobi',
        'company_tagline': cs.tagline if cs else 'Your Trusted Real Estate Partner',
        'currency': cs.currency_symbol if cs else 'KSh',
    })

    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.StringIO(html), result)
    if pdf.err:
        messages.error(request, 'Error generating receipt.')
        return redirect('payments:payment_detail', pk=payment.pk)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'filename="{payment.receipt_number}.pdf"'
    return response


@login_required
def payment_statement(request, sale_id):
    from apps.sales.models import Sale
    sale = get_object_or_404(Sale, pk=sale_id)
    if not (request.user.is_staff_or_above() or request.user.is_superuser) and sale.customer.user != request.user:
        messages.error(request, 'You do not have access to this statement.')
        return redirect('dashboard:home')

    from .services import get_customer_statement
    statement = get_customer_statement(sale.customer, sale)

    from apps.sales.utils import check_overdue_installments
    overdue_count = check_overdue_installments(sale=sale)
    if overdue_count:
        pass

    if request.GET.get('format') == 'pdf':
        from django.template.loader import render_to_string
        from xhtml2pdf import pisa
        import io

        company_name = 'Prime Lands Ltd'
        try:
            from apps.settings.models import CompanySetting
            cs = CompanySetting.objects.first()
            if cs:
                company_name = cs.company_name
        except Exception:
            pass

        html = render_to_string('payments/statement_pdf.html', {
            'statement': statement,
            'company_name': company_name,
            'company_tagline': cs.tagline if cs else 'Your Trusted Real Estate Partner',
            'company_address': cs.address if cs else '99 Westlands Rd, Nairobi',
            'company_phone': cs.phone if cs else '0728627678',
            'company_email': cs.email if cs else 'info@primelands.com',
            'currency': 'KSh',
        })
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.StringIO(html), result)
        if pdf.err:
            messages.error(request, 'Error generating statement PDF.')
            return redirect('payments:payment_statement', sale_id=sale_id)

        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'filename="statement_{sale.plot.plot_number}.pdf"'
        return response

    from apps.sales.models import InstallmentSchedule
    next_inst = InstallmentSchedule.objects.filter(
        sale=sale, status__in=['pending', 'partially_paid']
    ).order_by('due_date').first()

    template = 'payments/payment_statement.html' if request.user.is_staff_or_above() or request.user.is_superuser else 'payments/customer_payment_statement.html'
    return render(request, template, {
        'sale': sale,
        'statement': statement,
        'next_installment': next_inst,
        'is_staff': request.user.is_staff_or_above() or request.user.is_superuser,
    })


from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
import json


@login_required
def mpesa_payment(request):
    from apps.sales.models import Sale
    from apps.customers.models import Customer
    from .models import MpesaTransaction
    from .mpesa import stk_push

    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        if request.user.is_staff_or_above() or request.user.is_superuser:
            messages.error(request, 'Staff users cannot make M-Pesa payments. Switch to a customer account.')
            return redirect('dashboard:home')
        messages.warning(request, 'Please complete your customer profile first.')
        return redirect('accounts:profile')

    active_sales = Sale.objects.filter(customer=customer, status__in=['reservation', 'active'])

    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        amount = request.POST.get('amount')
        phone = request.POST.get('phone')

        if not sale_id or not amount or not phone:
            messages.error(request, 'All fields are required.')
            return redirect('payments:mpesa_payment')

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount.')
            return redirect('payments:mpesa_payment')

        sale = get_object_or_404(Sale, pk=sale_id, customer=customer)

        if amount > float(sale.balance):
            messages.error(request, f'Amount exceeds remaining balance of KSh {sale.balance:,.0f}.')
            return redirect('payments:mpesa_payment')

        from decimal import Decimal
        payment = Payment.objects.create(
            sale=sale,
            customer=customer,
            amount=Decimal(str(amount)),
            payment_method='mpesa',
            mpesa_phone=phone,
            payment_date=timezone.now().date(),
            status='pending',
        )

        account_ref = f'PLOT{sale.plot.plot_number}'[:12]
        response_data = stk_push(phone, int(round(amount)), account_ref)

        MpesaTransaction.objects.create(
            payment=payment,
            transaction_type='stk_push',
            merchant_request_id=response_data.get('MerchantRequestID', ''),
            checkout_request_id=response_data.get('CheckoutRequestID', ''),
            response_code=response_data.get('ResponseCode', '1'),
            response_description=response_data.get('ResponseDescription', ''),
            phone_number=phone,
            amount=Decimal(str(amount)),
            status='pending' if response_data.get('ResponseCode') == '0' else 'failed',
        )

        if response_data.get('ResponseCode') != '0':
            payment.status = 'failed'
            payment.save()
            messages.error(request, f'M-Pesa request failed: {response_data.get("ResponseDescription", "Unknown error")}')
            return redirect('payments:mpesa_payment')

        request.session['mpesa_checkout_id'] = response_data.get('CheckoutRequestID')
        request.session['mpesa_payment_id'] = payment.pk
        return render(request, 'payments/mpesa_processing.html', {
            'payment': payment,
            'checkout_id': response_data.get('CheckoutRequestID'),
            'simulated': response_data.get('_simulated', False),
        })

    return render(request, 'payments/mpesa_payment.html', {
        'active_sales': active_sales,
        'customer': customer,
    })


@login_required
def mpesa_complete(request):
    payment_id = request.session.pop('mpesa_payment_id', None)
    checkout_id = request.session.pop('mpesa_checkout_id', None)

    if not payment_id:
        messages.error(request, 'No pending payment found.')
        return redirect('payments:mpesa_payment')

    from .models import MpesaTransaction
    from .mpesa import simulate_callback
    from .services import process_payment

    payment = get_object_or_404(Payment, pk=payment_id, customer__user=request.user)

    try:
        mpesa_txn = MpesaTransaction.objects.get(payment=payment)
        callback_data = simulate_callback(checkout_id or mpesa_txn.checkout_request_id)
        body = callback_data['Body']['stkCallback']
        items = {i['Name']: i['Value'] for i in body.get('CallbackMetadata', {}).get('Item', [])}

        mpesa_txn.transaction_type = 'callback'
        mpesa_txn.result_code = body['ResultCode']
        mpesa_txn.result_description = body['ResultDesc']
        mpesa_txn.mpesa_receipt_number = items.get('MpesaReceiptNumber', '')
        mpesa_txn.transaction_date = timezone.now()
        mpesa_txn.raw_callback_data = callback_data
        mpesa_txn.status = 'success' if body['ResultCode'] == '0' else 'failed'
        mpesa_txn.save()

        if body['ResultCode'] == '0':
            payment.transaction_code = items.get('MpesaReceiptNumber', '')
            payment.mpesa_code = items.get('MpesaReceiptNumber', '')
            payment.save()
            process_payment(payment)
            messages.success(request, f'Payment of KSh {payment.amount:,.0f} confirmed successfully!')
        else:
            payment.status = 'failed'
            payment.save()
            messages.error(request, f'M-Pesa payment failed: {body["ResultDesc"]}')

    except Exception as e:
        messages.error(request, f'Error processing callback: {e}')

    return redirect('payments:payment_detail', pk=payment.pk)


@login_required
def mpesa_query_status(request):
    """Query M-Pesa STK Push status when callback was missed."""
    from .models import MpesaTransaction
    from .mpesa import query_stk_status

    payment_id = request.session.get('mpesa_payment_id')
    checkout_id = request.session.get('mpesa_checkout_id')

    if not payment_id or not checkout_id:
        messages.error(request, 'No pending payment to query.')
        return redirect('payments:mpesa_payment')

    try:
        payment = Payment.objects.get(pk=payment_id, customer__user=request.user)
    except Payment.DoesNotExist:
        messages.error(request, 'Payment not found.')
        return redirect('payments:mpesa_payment')

    if payment.status == 'completed':
        messages.info(request, 'This payment is already completed.')
        return redirect('payments:payment_detail', pk=payment.pk)

    response_data = query_stk_status(checkout_id)
    result_code = response_data.get('ResultCode', '1')

    if result_code == '0':
        from .services import process_payment
        try:
            mpesa_txn = MpesaTransaction.objects.get(payment=payment)
        except MpesaTransaction.DoesNotExist:
            messages.error(request, 'M-Pesa transaction record not found.')
            return redirect('payments:payment_detail', pk=payment.pk)

        receipt = response_data.get('Receipt', '') or response_data.get('MpesaReceiptNumber', '')
        if not receipt:
            receipt = 'QRY' + timezone.now().strftime('%y%m%d%H%M%S')

        mpesa_txn.result_code = result_code
        mpesa_txn.result_description = response_data.get('ResultDesc', 'Success')
        mpesa_txn.mpesa_receipt_number = receipt
        mpesa_txn.transaction_date = timezone.now()
        mpesa_txn.raw_callback_data = response_data
        mpesa_txn.status = 'success'
        mpesa_txn.save()

        payment.transaction_code = receipt
        payment.mpesa_code = receipt
        payment.status = 'pending'
        payment.save()

        process_payment(payment)
        messages.success(request, f'Payment of KSh {payment.amount:,.0f} confirmed via status query!')
        request.session.pop('mpesa_payment_id', None)
        request.session.pop('mpesa_checkout_id', None)
    else:
        desc = response_data.get('ResultDesc', 'Transaction not found or still pending')
        messages.warning(request, f'Payment not yet confirmed: {desc}')
        if 'RequestId' not in response_data:
            messages.info(request, 'Click "Complete Payment" to manually confirm if the payment was actually received.')

    return redirect('payments:payment_detail', pk=payment.pk)


@csrf_exempt
@require_POST
def mpesa_callback(request):
    from .models import MpesaTransaction
    from .services import process_payment

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)

    body = data.get('Body', {}).get('stkCallback', {})
    checkout_id = body.get('CheckoutRequestID', '')
    result_code = body.get('ResultCode', '1')
    result_desc = body.get('ResultDesc', '')

    try:
        mpesa_txn = MpesaTransaction.objects.get(checkout_request_id=checkout_id)
    except MpesaTransaction.DoesNotExist:
        return HttpResponse('Transaction not found', status=404)

    items = {i['Name']: i['Value'] for i in body.get('CallbackMetadata', {}).get('Item', [])}

    mpesa_txn.transaction_type = 'callback'
    mpesa_txn.result_code = result_code
    mpesa_txn.result_description = result_desc
    mpesa_txn.mpesa_receipt_number = items.get('MpesaReceiptNumber', '')
    mpesa_txn.transaction_date = timezone.now()
    mpesa_txn.raw_callback_data = data
    mpesa_txn.status = 'success' if result_code == '0' else 'failed'
    mpesa_txn.save()

    payment = mpesa_txn.payment
    if payment and result_code == '0':
        payment.transaction_code = items.get('MpesaReceiptNumber', '')
        payment.mpesa_code = items.get('MpesaReceiptNumber', '')
        payment.save()
        process_payment(payment)

    return HttpResponse('{"ResultCode":0,"ResultDesc":"Success"}', content_type='application/json')


@login_required
def mpesa_poll_status(request):
    """JSON endpoint for JS polling — returns payment status."""
    payment_id = request.session.get('mpesa_payment_id')
    if not payment_id:
        return JsonResponse({'status': 'no_payment'})

    try:
        payment = Payment.objects.get(pk=payment_id, customer__user=request.user)
        return JsonResponse({
            'status': payment.status,
            'payment_id': payment.pk,
            'redirect_url': reverse('payments:payment_detail', args=[payment.pk]),
        })
    except Payment.DoesNotExist:
        return JsonResponse({'status': 'not_found'})


@login_required
def staff_mpesa_query(request, pk):
    """Staff-only view to query M-Pesa status for any pending payment."""
    if not (request.user.is_staff_or_above() or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('dashboard:home')

    from .models import MpesaTransaction
    from .mpesa import query_stk_status

    payment = get_object_or_404(Payment, pk=pk)

    if payment.status != 'pending':
        messages.info(request, 'This payment is not pending.')
        return redirect('payments:payment_detail', pk=payment.pk)

    if payment.payment_method != 'mpesa':
        messages.error(request, 'This payment was not made via M-Pesa.')
        return redirect('payments:payment_detail', pk=payment.pk)

    try:
        mpesa_txn = MpesaTransaction.objects.get(payment=payment)
    except MpesaTransaction.DoesNotExist:
        messages.error(request, 'No M-Pesa transaction record found for this payment.')
        return redirect('payments:payment_detail', pk=payment.pk)

    if not mpesa_txn.checkout_request_id:
        messages.error(request, 'No CheckoutRequestID found. Cannot query M-Pesa.')
        return redirect('payments:payment_detail', pk=payment.pk)

    response_data = query_stk_status(mpesa_txn.checkout_request_id)
    result_code = response_data.get('ResultCode', '1')

    if result_code == '0':
        from .services import process_payment

        receipt = response_data.get('Receipt', '') or response_data.get('MpesaReceiptNumber', '')
        if not receipt:
            receipt = 'QRY' + timezone.now().strftime('%y%m%d%H%M%S')

        mpesa_txn.result_code = result_code
        mpesa_txn.result_description = response_data.get('ResultDesc', 'Success')
        mpesa_txn.mpesa_receipt_number = receipt
        mpesa_txn.transaction_date = timezone.now()
        mpesa_txn.raw_callback_data = response_data
        mpesa_txn.status = 'success'
        mpesa_txn.save()

        payment.transaction_code = receipt
        payment.mpesa_code = receipt
        payment.save()

        process_payment(payment, confirmed_by=request.user)
        messages.success(request, f'Payment confirmed via M-Pesa query! Receipt: {receipt}')
    else:
        desc = response_data.get('ResultDesc', 'Transaction not found or still pending')
        messages.warning(request, f'M-Pesa query returned: {desc}')

    return redirect('payments:payment_detail', pk=payment.pk)
