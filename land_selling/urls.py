from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from apps.views import serve_land_image

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
    # Serve land images from landImage directory
    path('landImage/<str:filename>', serve_land_image, name='serve_land_image'),
]

# Serve media files via Django (works in both dev and production)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
