from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.decorators import admin_required
from .models import CompanySetting, PageContent


@login_required
@admin_required
def settings_view(request):
    setting = CompanySetting.objects.first()
    if not setting:
        setting = CompanySetting.objects.create()

    if request.method == 'POST':
        from .forms import CompanySettingForm
        form = CompanySettingForm(request.POST, request.FILES, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved successfully.')
            return redirect('settings:settings')
    else:
        from .forms import CompanySettingForm
        form = CompanySettingForm(instance=setting)

    return render(request, 'settings/settings_form.html', {'form': form, 'title': 'Company Settings'})


@login_required
@admin_required
def page_content_list(request):
    pages = PageContent.objects.all()
    return render(request, 'settings/page_content_list.html', {'pages': pages})


@login_required
@admin_required
def page_content_edit(request, page):
    content, _ = PageContent.objects.get_or_create(page=page)
    if request.method == 'POST':
        from .forms import PageContentForm
        form = PageContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Page content updated.')
            return redirect('settings:page_content_list')
    else:
        from .forms import PageContentForm
        form = PageContentForm(instance=content)
    return render(request, 'settings/page_content_form.html', {'form': form, 'page': page})
