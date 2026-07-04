from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contact/inquiries/', views.contact_inquiries, name='contact_inquiries'),
    path('faq/', views.faq, name='faq'),
    path('hire-purchase/', views.hire_purchase, name='hire_purchase'),
    path('blog/', views.blog, name='blog'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
