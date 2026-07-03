from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.role == 'customer':
            path = request.path_info
            allowed_paths = [
                reverse('customers:customer_profile'),
                reverse('accounts:logout'),
                reverse('accounts:login'),
                '/static/',
                '/media/',
            ]
            if not any(path.startswith(p) for p in allowed_paths):
                from apps.customers.models import Customer
                try:
                    customer = Customer.objects.get(user=request.user)
                    if not customer.address or not customer.phone or not customer.national_id:
                        return redirect('customers:customer_profile')
                except Customer.DoesNotExist:
                    return redirect('customers:customer_profile')
        return self.get_response(request)


class VerificationRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.role == 'customer':
            path = request.path_info
            allowed_paths = [
                reverse('customers:customer_profile'),
                reverse('customers:awaiting_verification'),
                reverse('accounts:logout'),
                reverse('accounts:login'),
                '/static/',
                '/media/',
            ]
            if not any(path.startswith(p) for p in allowed_paths):
                from apps.customers.models import Customer
                try:
                    customer = Customer.objects.get(user=request.user)
                    if not customer.is_verified:
                        return redirect('customers:awaiting_verification')
                except Customer.DoesNotExist:
                    pass
        return self.get_response(request)