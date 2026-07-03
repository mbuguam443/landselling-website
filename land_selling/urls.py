from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.http import FileResponse, Http404
import os

def media_serve(request, path):
    file_path = settings.MEDIA_ROOT / path
    if not os.path.exists(file_path):
        file_path = settings.BASE_DIR / 'landImage' / path
    if not os.path.exists(file_path):
        raise Http404('File not found')
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = 'image/jpeg' if path.lower().endswith(('.jpg', '.jpeg')) else \
                               'image/png' if path.lower().endswith('.png') else \
                               'image/svg+xml' if path.lower().endswith('.svg') else \
                               'application/pdf' if path.lower().endswith('.pdf') else \
                               'application/octet-stream'
    return response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.website.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('projects/', include('apps.projects.urls')),
    path('plots/', include('apps.plots.urls')),
    path('customers/', include('apps.customers.urls')),
    path('sales/', include('apps.sales.urls')),
    path('payments/', include('apps.payments.urls')),
    path('documents/', include('apps.documents.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('reports/', include('apps.reports.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('settings/', include('apps.settings.urls')),
    path('subscriptions/', include('apps.subscriptions.urls')),
]

urlpatterns += [re_path(r'^media/(?P<path>.*)$', media_serve)]
