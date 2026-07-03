from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_dashboard, name='report_dashboard'),
    path('sales/', views.sales_report, name='sales_report'),
    path('payments/', views.payments_report, name='payments_report'),
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('customers/', views.customers_report, name='customers_report'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('export/<str:report_type>/<str:format>/', views.export_report, name='export_report'),
]
