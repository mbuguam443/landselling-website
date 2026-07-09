from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('<int:pk>/', views.payment_detail, name='payment_detail'),
    path('create/', views.payment_create, name='payment_create'),
    path('<int:pk>/confirm/', views.payment_confirm, name='payment_confirm'),
    path('<int:pk>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('statement/<int:sale_id>/', views.payment_statement, name='payment_statement'),
    path('mpesa/pay/', views.mpesa_payment, name='mpesa_payment'),
    path('mpesa/complete/', views.mpesa_complete, name='mpesa_complete'),
    path('mpesa/query-status/', views.mpesa_query_status, name='mpesa_query_status'),
    path('mpesa/query-status/<int:pk>/', views.staff_mpesa_query, name='staff_mpesa_query'),
    path('mpesa/poll-status/', views.mpesa_poll_status, name='mpesa_poll_status'),
    path('mpesa/stk-push/', views.mpesa_stk_push_ajax, name='mpesa_stk_push_ajax'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
]
