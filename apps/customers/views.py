from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import staff_required
from apps.reports.utils import log_audit
from .models import Customer
from .forms import CustomerForm, CustomerProfileForm


@login_required
@staff_required
def customer_list(request):
    from apps.core.utils import get_sortable_context
    customers_list = Customer.objects.select_related('user').all()
    ctx = get_sortable_context(request, customers_list, default_sort='-created_at',
                               allowed_fields=['name', 'email', 'phone', 'city', 'is_verified', 'created_at'],
                               search_fields=['name', 'email', 'phone', 'city'],
                               per_page=15)
    return render(request, 'customers/customer_list.html', ctx)


@login_required
@staff_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer.objects.select_related('user'), pk=pk)
    return render(request, 'customers/customer_detail.html', {'customer': customer})


@login_required
@staff_required
def customer_create(request):
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save()
            log_audit(request.user, 'create', model_name='Customer', object_id=customer.pk,
                      object_repr=customer.name, description=f'Customer {customer.name} created', request=request)
            messages.success(request, 'Customer created successfully.')
            return redirect('customers:customer_detail', pk=customer.pk)
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Create Customer'})


@login_required
@staff_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('customers:customer_detail', pk=customer.pk)
    return render(request, 'customers/customer_form.html', {'form': form, 'title': 'Edit Customer'})


@login_required
def customer_profile(request):
    customer, _ = Customer.objects.get_or_create(user=request.user)
    was_incomplete = not customer.address or not customer.phone or not customer.national_id
    form = CustomerProfileForm(instance=customer)
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            now_complete = bool(customer.address and customer.phone and customer.national_id)
            if was_incomplete and now_complete:
                from apps.notifications.services import notify_staff_verification_ready
                notify_staff_verification_ready(customer.name, customer.id)
            messages.success(request, 'Profile details saved successfully.')
            return redirect('customers:customer_profile')
    return render(request, 'customers/customer_profile.html', {
        'form': form,
        'customer': customer,
    })


@login_required
@staff_required
def customer_verify_list(request):
    from apps.core.utils import get_sortable_context
    unverified = Customer.objects.filter(is_verified=False).select_related('user')
    verified = Customer.objects.filter(is_verified=True).select_related('user')
    ctx = get_sortable_context(request, unverified, default_sort='-created_at',
                               allowed_fields=['name', 'email', 'phone', 'created_at'],
                               search_fields=['name', 'email', 'phone'],
                               per_page=15)
    ctx['verified'] = verified
    return render(request, 'customers/customer_verify_list.html', ctx)


@login_required
@staff_required
def customer_verify(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.is_verified = True
    customer.save()
    customer.user.is_verified = True
    customer.user.save()
    messages.success(request, f'{customer.name} has been verified.')
    return redirect('customers:customer_detail', pk=customer.pk)


@login_required
@staff_required
def customer_unverify(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.is_verified = False
    customer.save()
    customer.user.is_verified = False
    customer.user.save()
    messages.warning(request, f'{customer.name} verification has been revoked.')
    return redirect('customers:customer_detail', pk=customer.pk)


@login_required
def awaiting_verification(request):
    return render(request, 'customers/awaiting_verification.html')
