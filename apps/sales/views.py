from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import staff_required
from apps.reports.utils import log_audit
from apps.notifications.services import notify_sale
from .models import Sale, Reservation
from .forms import SaleForm, ReservationForm


@login_required
@staff_required
def sale_list(request):
    from apps.core.utils import get_sortable_context
    sales_list = Sale.objects.select_related('customer__user', 'plot__project', 'sales_agent').all()
    ctx = get_sortable_context(request, sales_list, default_sort='-sale_date',
                               allowed_fields=['customer__name', 'plot__plot_number', 'selling_price', 'status', 'sale_date'],
                               search_fields=['customer__name', 'plot__plot_number', 'status'],
                               per_page=15)
    return render(request, 'sales/sale_list.html', ctx)


@login_required
def customer_sale_list(request):
    from apps.core.utils import get_sortable_context
    from apps.customers.models import Customer
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        messages.error(request, 'Complete your customer profile first.')
        return redirect('customers:customer_profile')
    sales_list = Sale.objects.filter(customer=customer).select_related('plot__project')
    ctx = get_sortable_context(request, sales_list, default_sort='-sale_date',
                               allowed_fields=['plot__plot_number', 'selling_price', 'status', 'sale_date'],
                               search_fields=['plot__plot_number', 'status'],
                               per_page=10)
    return render(request, 'sales/customer_sale_list.html', ctx)


@login_required
@staff_required
def sale_detail(request, pk):
    sale = get_object_or_404(
        Sale.objects.select_related('customer__user', 'plot__project', 'sales_agent')
        .prefetch_related('payments', 'schedule'),
        pk=pk
    )
    from apps.sales.utils import check_overdue_installments
    check_overdue_installments(sale=sale)
    sale.refresh_from_db()
    return render(request, 'sales/sale_detail.html', {'sale': sale})


@login_required
@staff_required
def sale_create(request):
    form = SaleForm()
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            if request.user.role in ('super_admin', 'administrator'):
                from apps.accounts.models import User
                fallback_agent = User.objects.filter(role='sales_agent', is_active=True).first()
                sale.sales_agent = fallback_agent
            else:
                sale.sales_agent = request.user
            sale.monthly_installment = sale.plot.monthly_installment(sale.installment_months)
            sale.save()
            log_audit(request.user, 'sale', model_name='Sale', object_id=sale.pk,
                      object_repr=str(sale), description=f'Sale created for {sale.customer.name}', request=request)
            notify_sale(sale.customer.user, sale.plot.plot_number)
            messages.success(request, 'Sale created successfully.')
            return redirect('sales:sale_detail', pk=sale.pk)
    return render(request, 'sales/sale_form.html', {'form': form, 'title': 'Create Sale'})


@login_required
@staff_required
def sale_edit(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    form = SaleForm(instance=sale)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sale updated successfully.')
            return redirect('sales:sale_detail', pk=sale.pk)
    return render(request, 'sales/sale_form.html', {'form': form, 'title': 'Edit Sale'})


@login_required
@staff_required
def reservation_list(request):
    from apps.core.utils import get_sortable_context
    reservations = Reservation.objects.select_related('customer__user', 'plot__project', 'reserved_by').all()
    ctx = get_sortable_context(request, reservations, default_sort='-reservation_date',
                               allowed_fields=['customer__name', 'plot__plot_number', 'status', 'reservation_date'],
                               search_fields=['customer__name', 'plot__plot_number', 'status'],
                               per_page=15)
    return render(request, 'sales/reservation_list.html', ctx)


@login_required
def reservation_create(request):
    from django.utils import timezone
    from datetime import timedelta
    from apps.customers.models import Customer
    initial = {}
    plot_id = request.GET.get('plot')
    if plot_id:
        initial['plot'] = plot_id
    if not request.user.is_staff_or_above():
        try:
            customer = Customer.objects.get(user=request.user)
            if not customer.is_verified:
                messages.error(request, 'Your account must be verified before booking a plot. Complete your profile and wait for verification.')
                return redirect('customers:customer_profile')
            initial['customer'] = customer.id
        except Customer.DoesNotExist:
            messages.error(request, 'Complete your customer profile first.')
            return redirect('customers:customer_profile')

    form = ReservationForm(user=request.user, initial=initial)
    if request.method == 'POST':
        form = ReservationForm(request.POST, user=request.user)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.reserved_by = request.user
            if not request.user.is_staff_or_above():
                reservation.expiry_date = timezone.now() + timedelta(days=7)
                reservation.amount = 0
            reservation.save()
            reservation.plot.status = 'reserved'
            reservation.plot.save()
            log_audit(request.user, 'create', model_name='Reservation', object_id=reservation.pk,
                      object_repr=str(reservation), description=f'Reservation for {reservation.customer.name}', request=request)
            from apps.notifications.services import create_notification
            create_notification(
                recipient=reservation.customer.user,
                notification_type='support',
                title='Reservation Submitted',
                message=f'Your booking for plot {reservation.plot.plot_number} has been submitted and is pending confirmation.',
                link='/sales/',
            )
            from apps.accounts.models import User
            staff_roles = ['super_admin', 'administrator', 'finance_officer', 'sales_agent', 'customer_care']
            for staff in User.objects.filter(role__in=staff_roles):
                create_notification(
                    recipient=staff,
                    notification_type='support',
                    title='New Reservation',
                    message=f'{reservation.customer.name} booked plot {reservation.plot.plot_number}.',
                    link='/sales/reservations/',
                )
            messages.success(request, 'Reservation submitted successfully.')
            if request.user.is_staff_or_above():
                return redirect('sales:reservation_list')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    template = 'sales/reservation_form.html' if request.user.is_staff_or_above() else 'sales/customer_reservation_form.html'
    return render(request, template, {'form': form, 'title': 'Book a Plot'})


@login_required
@staff_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(
        Reservation.objects.select_related('customer__user', 'plot__project', 'reserved_by'),
        pk=pk
    )
    return render(request, 'sales/reservation_detail.html', {'reservation': reservation})


@login_required
@staff_required
def reservation_convert(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.status != 'active':
        messages.error(request, 'Only active reservations can be converted.')
        return redirect('sales:reservation_detail', pk=pk)

    if not reservation.customer.is_verified:
        messages.error(request, f'Cannot convert: {reservation.customer.name} is not verified. Please verify the customer first.')
        return render(request, 'sales/reservation_convert.html', {
            'reservation': reservation,
            'default_deposit': reservation.plot.price * 20 // 100,
        })

    if request.method == 'POST':
        from django.utils import timezone
        from decimal import Decimal
        deposit = request.POST.get('deposit_amount', '0')
        months = request.POST.get('installment_months', '60')
        try:
            deposit = Decimal(deposit)
            months = int(months)
        except Exception:
            messages.error(request, 'Invalid deposit amount or installment months.')
            return redirect('sales:reservation_convert', pk=pk)

        if request.user.role in ('super_admin', 'administrator'):
            from apps.accounts.models import User
            fallback_agent = User.objects.filter(role='sales_agent', is_active=True).first()
            agent_for_sale = fallback_agent
        else:
            agent_for_sale = request.user
        sale = Sale.objects.create(
            customer=reservation.customer,
            plot=reservation.plot,
            selling_price=reservation.plot.price,
            deposit_amount=deposit,
            installment_months=months,
            sales_agent=agent_for_sale,
            sale_date=timezone.now().date(),
            status='active',
        )
        reservation.status = 'converted'
        reservation.save()

        reservation.plot.status = 'sold'
        reservation.plot.save()

        notify_sale(sale.customer.user, sale.plot.plot_number)

        from apps.notifications.services import create_notification
        from apps.accounts.models import User
        staff_roles = ['super_admin', 'administrator', 'finance_officer', 'sales_agent', 'customer_care']
        for staff in User.objects.filter(role__in=staff_roles):
            create_notification(
                recipient=staff,
                notification_type='sale',
                title='Reservation Converted',
                message=f'{reservation.customer.name}\'s reservation for {reservation.plot.plot_number} converted to sale.',
                link='/sales/',
            )

        log_audit(request.user, 'create', model_name='Sale', object_id=sale.pk,
                  object_repr=str(sale), description=f'Sale from reservation {pk}', request=request)
        messages.success(request, f'Reservation converted to sale #{sale.pk}.')
        return redirect('sales:sale_detail', pk=sale.pk)

    return render(request, 'sales/reservation_convert.html', {
        'reservation': reservation,
        'default_deposit': reservation.plot.price * 20 // 100,
    })


@login_required
@staff_required
def reservation_cancel(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.status != 'active':
        messages.error(request, 'Reservation is already closed.')
        return redirect('sales:reservation_detail', pk=pk)

    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()

        reservation.plot.status = 'available'
        reservation.plot.save()

        from apps.notifications.services import create_notification
        create_notification(
            recipient=reservation.customer.user,
            notification_type='support',
            title='Reservation Cancelled',
            message=f'Your reservation for plot {reservation.plot.plot_number} has been cancelled.',
            link='/sales/',
        )

        log_audit(request.user, 'update', model_name='Reservation', object_id=reservation.pk,
                  object_repr=str(reservation), description=f'Reservation cancelled by {request.user}', request=request)
        messages.success(request, 'Reservation cancelled.')
        return redirect('sales:reservation_list')

    return render(request, 'sales/reservation_confirm_delete.html',
                  {'reservation': reservation, 'action': 'cancel'})
