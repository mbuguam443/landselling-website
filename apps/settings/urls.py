from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_view, name='settings'),
    path('pages/', views.page_content_list, name='page_content_list'),
    path('pages/<str:page>/', views.page_content_edit, name='page_content_edit'),
]
