from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Plans (admin)
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:pk>/edit/', views.plan_edit, name='plan_edit'),

    # Subscriptions (admin view all)
    path('', views.subscription_list, name='subscription_list'),

    # Staff: my subscription
    path('my/', views.my_subscription, name='my_subscription'),
    path('subscribe/<int:plan_id>/', views.subscribe_to_plan, name='subscribe_to_plan'),

    # Payments
    path('payments/', views.sub_payment_list, name='sub_payment_list'),
    path('payments/<int:pk>/confirm/', views.confirm_sub_payment, name='confirm_sub_payment'),
]
