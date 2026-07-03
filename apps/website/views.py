from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
    })


def about(request):
    content = PageContent.objects.filter(page='about').first()
    return render(request, 'website/about.html', {'content': content})


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
    return render(request, 'website/contact.html')


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
    return render(request, 'website/faq.html', {'content': content})


def hire_purchase(request):
    content = PageContent.objects.filter(page='hire_purchase').first()
    return render(request, 'website/hire_purchase.html', {'content': content})


def blog(request):
    return render(request, 'website/blog.html')


def testimonials(request):
    return render(request, 'website/testimonials.html')
