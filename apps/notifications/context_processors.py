def unread_notifications(request):
    ctx = {'unread_count': 0, 'recent_notifications': [],
           'pending_verification_count': 0, 'pending_payment_count': 0}
    if request.user.is_authenticated:
        from .models import Notification
        ctx['unread_count'] = Notification.objects.filter(recipient=request.user, is_read=False).count()
        ctx['recent_notifications'] = Notification.objects.filter(recipient=request.user)[:5]
        if request.user.is_staff_or_above() or request.user.is_superuser:
            from apps.customers.models import Customer
            ctx['pending_verification_count'] = Customer.objects.filter(is_verified=False).count()
            from apps.payments.models import Payment
            ctx['pending_payment_count'] = Payment.objects.filter(status='pending').count()
    return ctx
