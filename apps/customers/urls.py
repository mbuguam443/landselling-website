from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('<int:pk>/', views.customer_detail, name='customer_detail'),
    path('create/', views.customer_create, name='customer_create'),
    path('<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('verify/', views.customer_verify_list, name='customer_verify_list'),
    path('<int:pk>/verify/', views.customer_verify, name='customer_verify'),
    path('<int:pk>/unverify/', views.customer_unverify, name='customer_unverify'),
    path('awaiting-verification/', views.awaiting_verification, name='awaiting_verification'),
]
