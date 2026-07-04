from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from apps.accounts.decorators import staff_required
from apps.plots.models import Plot
from apps.projects.models import Project
from apps.settings.models import PageContent
from apps.accounts.models import User
from apps.notifications.services import create_notification
from .forms import ContactForm
from .models import ContactMessage


def home(request):
    featured_projects = Project.objects.filter(featured=True)[:4]
    featured_plots = Plot.objects.filter(featured=True, status='available').select_related('project')[:6]
    stats = {
        'projects': Project.objects.count(),
        'plots': Plot.objects.count(),
        'sold': Plot.objects.filter(status='sold').count(),
        'customers': 0,
    }
    from apps.customers.models import Customer
    stats['customers'] = Customer.objects.count()

    return render(request, 'website/home.html', {
        'featured_projects': featured_projects,
        'featured_plots': featured_plots,
        'stats': stats,
        'meta_description': 'Prime Lands Ltd - Kenya\'s trusted real estate company. Buy prime land with flexible installment plans, verified plots, and guaranteed title deeds in Nairobi and beyond.',
        'og_title': 'Prime Lands Ltd - Buy Land in Kenya with Flexible Installments',
        'og_description': 'Discover prime land for sale in Kenya. Affordable plots with flexible payment plans and guaranteed title deeds.',
    })


def about(request):
    content = PageContent.objects.filter(page='about').first()
    return render(request, 'website/about.html', {
        'content': content,
        'meta_description': 'Learn about Prime Lands Ltd - Kenya\'s premier real estate company dedicated to making land ownership accessible through flexible payment plans and exceptional service.',
        'og_title': 'About Us - Prime Lands Ltd',
        'og_description': 'Discover Prime Lands Ltd - your trusted partner in Kenyan real estate with years of experience in land sales and customer satisfaction.',
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            msg = form.save()
            for admin in User.objects.exclude(role='customer'):
                create_notification(
                    recipient=admin,
                    notification_type='support',
                    title='New Contact Inquiry',
                    message=f'New message from {form.cleaned_data.get("name", "Unknown")}',
                    link='/contact/inquiries/',
                )
            messages.success(request, 'Thank you for your message. We will get back to you shortly.')
        else:
            messages.error(request, 'Please correct the errors below.')
        return redirect('website:contact')
    return render(request, 'website/contact.html', {
        'meta_description': 'Contact Prime Lands Ltd for inquiries about land for sale in Kenya. Reach us via phone, email, or visit our office in Westlands, Nairobi.',
        'og_title': 'Contact Us - Prime Lands Ltd',
        'og_description': 'Get in touch with Prime Lands Ltd for land purchase inquiries, site visits, and customer support.',
    })


@login_required
@staff_required
def contact_inquiries(request):
    from apps.core.utils import get_sortable_context
    inquiries = ContactMessage.objects.all()
    ctx = get_sortable_context(request, inquiries, default_sort='-created_at',
                               allowed_fields=['name', 'email', 'subject', 'is_read', 'created_at'],
                               search_fields=['name', 'email', 'subject'],
                               per_page=15)
    return render(request, 'website/contact_inquiries.html', ctx)


def faq(request):
    content = PageContent.objects.filter(page='faq').first()
    return render(request, 'website/faq.html', {
        'content': content,
        'meta_description': 'Frequently asked questions about buying land in Kenya with Prime Lands Ltd. Learn about payments, installments, title deeds, and site visits.',
        'og_title': 'FAQs - Prime Lands Ltd',
        'og_description': 'Get answers to common questions about purchasing land, payment methods, installment plans, and title deeds at Prime Lands Ltd.',
    })


def hire_purchase(request):
    content = PageContent.objects.filter(page='hire_purchase').first()
    return render(request, 'website/hire_purchase.html', {
        'content': content,
        'meta_description': 'Buy land through hire purchase at Prime Lands Ltd. Pay affordable monthly installments and own your dream plot with a guaranteed title deed.',
        'og_title': 'Hire Purchase - Buy Land with Installments | Prime Lands Ltd',
        'og_description': 'Own your dream land with affordable monthly installments. Zero interest options available with Prime Lands Ltd.',
    })


def blog(request):
    return render(request, 'website/blog.html', {
        'meta_description': 'Read the latest news, insights, and guides about real estate and land investment in Kenya from Prime Lands Ltd.',
        'og_title': 'Blog - Prime Lands Ltd',
        'og_description': 'Stay updated with the latest real estate news, land buying tips, and investment guides from Prime Lands Ltd.',
    })


def testimonials(request):
    return render(request, 'website/testimonials.html', {
        'meta_description': 'Read what our customers say about buying land with Prime Lands Ltd. Real reviews from satisfied landowners across Kenya.',
        'og_title': 'Testimonials - Prime Lands Ltd',
        'og_description': 'Hear from our satisfied customers who have successfully purchased land through Prime Lands Ltd.',
    })


def robots_txt(request):
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /dashboard/
Disallow: /customers/
Disallow: /sales/
Disallow: /payments/
Disallow: /documents/
Disallow: /notifications/
Disallow: /reports/
Disallow: /settings/
Disallow: /subscriptions/

Sitemap: {scheme}://{host}/sitemap.xml
""".format(scheme=request.scheme, host=request.get_host())
    return HttpResponse(content, content_type='text/plain')
