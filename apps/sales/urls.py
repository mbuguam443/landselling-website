from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='sale_list'),
    path('my-purchases/', views.customer_sale_list, name='customer_sale_list'),
    path('<int:pk>/', views.sale_detail, name='sale_detail'),
    path('create/', views.sale_create, name='sale_create'),
    path('<int:pk>/edit/', views.sale_edit, name='sale_edit'),
    path('reservations/', views.reservation_list, name='reservation_list'),
    path('reservations/create/', views.reservation_create, name='reservation_create'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:pk>/convert/', views.reservation_convert, name='reservation_convert'),
    path('reservations/<int:pk>/cancel/', views.reservation_cancel, name='reservation_cancel'),
]
