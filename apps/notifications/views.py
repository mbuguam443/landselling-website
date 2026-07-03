from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification


@login_required
def notification_list(request):
    from apps.core.utils import get_sortable_context
    notifications = Notification.objects.filter(recipient=request.user)
    ctx = get_sortable_context(request, notifications, default_sort='-created_at',
                               allowed_fields=['title', 'notification_type', 'is_read', 'created_at'],
                               search_fields=['title', 'notification_type'],
                               per_page=20)
    return render(request, 'notifications/notification_list.html', ctx)


@login_required
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:notification_list')


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:notification_list')
