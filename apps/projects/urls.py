from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<slug:slug>/', views.project_detail, name='project_detail'),
    path('<slug:slug>/edit/', views.project_edit, name='project_edit'),
    path('<slug:slug>/delete/', views.project_delete, name='project_delete'),
]
