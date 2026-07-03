from django.contrib import admin
from .models import CompanySetting, PageContent

@admin.register(CompanySetting)
class CompanySettingAdmin(admin.ModelAdmin):
    pass

@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ['page', 'title', 'updated_at']
