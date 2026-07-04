from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models as db_models
from apps.accounts.decorators import staff_required, admin_required
from .models import SubscriptionPlan, Subscription, SubscriptionPayment


# --- Admin: Plan CRUD ---

@login_required
@admin_required
def plan_list(request):
    from apps.core.utils import get_sortable_context
    plans = SubscriptionPlan.objects.all()
    ctx = get_sortable_context(request, plans, default_sort='price',
                               allowed_fields=['name', 'price', 'duration_days', 'is_active'],
                               search_fields=['name', 'description'])
    return render(request, 'subscriptions/plan_list.html', ctx)


@login_required
@admin_required
def plan_create(request):
    if request.method == 'POST':
        from .forms import SubscriptionPlanForm
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscription plan created.')
            return redirect('subscriptions:plan_list')
    else:
        from .forms import SubscriptionPlanForm
        form = SubscriptionPlanForm()
    return render(request, 'subscriptions/plan_form.html', {'form': form, 'title': 'Create Plan'})


@login_required
@admin_required
def plan_edit(request, pk):
    plan = get_object_or_404(SubscriptionPlan, pk=pk)
    if request.method == 'POST':
        from .forms import SubscriptionPlanForm
        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan updated.')
            return redirect('subscriptions:plan_list')
    else:
        from .forms import SubscriptionPlanForm
        form = SubscriptionPlanForm(instance=plan)
    return render(request, 'subscriptions/plan_form.html', {'form': form, 'title': 'Edit Plan'})


# --- Admin: Subscription list ---

@login_required
@staff_required
def subscription_list(request):
    from apps.core.utils import get_sortable_context
    subs = Subscription.objects.select_related('user', 'plan').all()
    ctx = get_sortable_context(request, subs, default_sort='-start_date',
                               allowed_fields=['user__username', 'plan__name', 'start_date', 'end_date', 'is_active'],
                               search_fields=['user__username', 'user__email', 'plan__name', 'notes'])
    return render(request, 'subscriptions/subscription_list.html', ctx)


# --- Staff: My subscription ---

@login_required
@staff_required
def my_subscription(request):
    if request.user.role in ('super_admin', 'administrator'):
        messages.error(request, 'Admins do not have subscriptions.')
        return redirect('reports:revenue_report')
    from django.utils import timezone
    active_sub = Subscription.objects.filter(user=request.user, is_active=True, end_date__gte=timezone.now().date()).first()
    sub_history = Subscription.objects.filter(user=request.user).order_by('-start_date')
    plans = SubscriptionPlan.objects.filter(is_active=True)
    return render(request, 'subscriptions/my_subscription.html', {
        'active_sub': active_sub,
        'sub_history': sub_history,
        'plans': plans,
    })


@login_required
@staff_required
def subscribe_to_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, pk=plan_id, is_active=True)
    from django.utils import timezone
    now = timezone.now().date()

    # Block if agent already has ANY active subscription (even if expired but not yet deactivated)
    active = Subscription.objects.filter(user=request.user, is_active=True).first()
    if active:
        messages.info(request, f'You already have an active subscription ({active.plan}) until {active.end_date}.')
        return redirect('subscriptions:my_subscription')

    # Deactivate any old subscriptions that should have expired
    Subscription.objects.filter(
        user=request.user, is_active=True, end_date__lt=now
    ).update(is_active=False)

    end_date = now + timezone.timedelta(days=plan.duration_days)
    sub = Subscription.objects.create(
        user=request.user,
        plan=plan,
        start_date=now,
        end_date=end_date,
        is_active=True,
    )
    # Percentage plans auto-activate (no payment needed)
    if plan.plan_type == 'percentage':
        messages.success(request, f'Subscribed to {plan.name}. Commission of {plan.commission_percentage}% will apply to your sales.')
    else:
        SubscriptionPayment.objects.create(
            subscription=sub,
            user=request.user,
            amount=plan.price,
            payment_method='mpesa',
            status='pending',
        )
        messages.success(request, f'Subscribed to {plan.name}. Please complete payment.')
    return redirect('subscriptions:my_subscription')


# --- Admin: Subscription payment list ---

@login_required
@staff_required
def sub_payment_list(request):
    from apps.core.utils import get_sortable_context
    payments = SubscriptionPayment.objects.select_related('subscription', 'user').all()
    ctx = get_sortable_context(request, payments, default_sort='-payment_date',
                               allowed_fields=['user__username', 'amount', 'status', 'payment_date', 'payment_method'],
                               search_fields=['user__username', 'transaction_ref', 'receipt_number', 'notes'])
    return render(request, 'subscriptions/sub_payment_list.html', ctx)


@login_required
@admin_required
def confirm_sub_payment(request, pk):
    payment = get_object_or_404(SubscriptionPayment, pk=pk, status='pending')
    payment.status = 'confirmed'
    payment.confirmed_by = request.user
    payment.save()
    messages.success(request, 'Subscription payment confirmed.')
    return redirect('subscriptions:sub_payment_list')


@login_required
@admin_required
def sub_payment_create(request):
    from django.utils import timezone
    from .forms import SubscriptionPaymentForm

    if request.method == 'POST':
        form = SubscriptionPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.confirmed_by = request.user
            payment.status = 'confirmed'
            payment.receipt_number = f'SUB-{timezone.now().strftime("%Y%m%d")}-{payment.pk or "0001"}'
            payment.save()
            messages.success(request, f'Payment of KSh {payment.amount} recorded for {payment.user.get_full_name() or payment.user.username}.')
            return redirect('subscriptions:sub_payment_list')
    else:
        form = SubscriptionPaymentForm()

    return render(request, 'subscriptions/sub_payment_form.html', {'form': form})


@login_required
@admin_required
def subscription_switch(request, pk):
    sub = get_object_or_404(Subscription, pk=pk)
    from django.utils import timezone
    now = timezone.now().date()

    if request.method == 'POST':
        new_plan_id = request.POST.get('new_plan_id')
        if not new_plan_id:
            messages.error(request, 'Please select a new plan.')
            return redirect('subscriptions:subscription_switch', pk=pk)

        new_plan = get_object_or_404(SubscriptionPlan, pk=new_plan_id, is_active=True)

        # Deactivate old subscription
        sub.is_active = False
        sub.notes = f'Switched to {new_plan.name} by {request.user.username} on {now}'
        sub.save()

        # Create new subscription
        end_date = now + timezone.timedelta(days=new_plan.duration_days)
        new_sub = Subscription.objects.create(
            user=sub.user,
            plan=new_plan,
            start_date=now,
            end_date=end_date,
            is_active=True,
            notes=f'Switched from {sub.plan.name} by {request.user.username}',
        )

        # Create payment record for fixed plans
        if new_plan.plan_type == 'fixed':
            SubscriptionPayment.objects.create(
                subscription=new_sub,
                user=sub.user,
                amount=new_plan.price,
                payment_method='mpesa',
                status='confirmed',
                confirmed_by=request.user,
                notes=f'Admin switch from {sub.plan.name}',
            )

        messages.success(request, f'{sub.user.get_full_name() or sub.user.username} switched from {sub.plan.name} to {new_plan.name}.')
        return redirect('subscriptions:subscription_list')

    plans = SubscriptionPlan.objects.filter(is_active=True).exclude(pk=sub.plan_id)
    return render(request, 'subscriptions/subscription_switch.html', {
        'subscription': sub,
        'plans': plans,
    })
