from django.urls import path
from . import views

app_name = 'plots'

urlpatterns = [
    path('', views.plot_list, name='plot_list'),
    path('create/', views.plot_create, name='plot_create'),
    path('<int:pk>/', views.plot_detail, name='plot_detail'),
    path('<int:pk>/edit/', views.plot_edit, name='plot_edit'),
    path('<int:pk>/delete/', views.plot_delete, name='plot_delete'),
]
