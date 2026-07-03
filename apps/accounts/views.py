from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from .forms import LoginForm, RegistrationForm, ProfileUpdateForm
from .decorators import role_required
from apps.reports.utils import log_audit


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            log_audit(user, 'login', description='User logged in', request=request)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard:home'
            return redirect(next_url)
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'customer':
                from apps.customers.models import Customer
                Customer.objects.get_or_create(
                    user=user,
                    defaults={'phone': user.phone or ''}
                )
            log_audit(user, 'create', model_name='User', object_id=user.id,
                      object_repr=user.username, description='Account registered', request=request)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            if user.role == 'customer':
                return redirect('customers:customer_profile')
            return redirect('dashboard:home')
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        log_audit(request.user, 'logout', description='User logged out', request=request)
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('website:home')


@login_required
def profile_view(request):
    if request.user.role == 'customer':
        return redirect('customers:customer_profile')
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            if user.role == 'customer':
                from apps.customers.models import Customer
                Customer.objects.get_or_create(
                    user=user,
                    defaults={'phone': user.phone or ''}
                )
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
@role_required(['super_admin', 'administrator'])
def user_list(request):
    from apps.core.utils import get_sortable_context
    from .models import User
    users = User.objects.all()
    ctx = get_sortable_context(request, users, default_sort='-date_joined',
                               allowed_fields=['username', 'email', 'role', 'is_active', 'date_joined'],
                               search_fields=['username', 'email', 'role'],
                               per_page=15)
    return render(request, 'accounts/user_list.html', ctx)


@login_required
@role_required(['super_admin', 'administrator'])
def user_create(request):
    from .models import User
    from django.contrib.auth.hashers import make_password
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        password = request.POST.get('password')
        if not all([username, password]):
            messages.error(request, 'Username and password are required.')
            return render(request, 'accounts/user_form.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'accounts/user_form.html')
        user = User.objects.create(
            username=username,
            email=email or '',
            first_name=first_name or '',
            last_name=last_name or '',
            role=role or 'customer',
            is_staff=True,
            is_active=True,
        )
        user.password = make_password(password)
        user.save()
        messages.success(request, f'User "{username}" created successfully.')
        from apps.reports.utils import log_audit
        log_audit(request.user, 'User Created', f'Created user: {username} ({role})')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html')


@login_required
@role_required(['super_admin', 'administrator'])
def user_detail(request, pk):
    from .models import User
    user = User.objects.get(pk=pk)
    return render(request, 'accounts/user_detail.html', {'user_obj': user})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})
