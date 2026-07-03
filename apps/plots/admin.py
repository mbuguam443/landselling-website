from django.contrib import admin
from .models import Plot, PlotImage

@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ['plot_number', 'project', 'size_sqm', 'price', 'status']
    list_filter = ['status', 'project']

@admin.register(PlotImage)
class PlotImageAdmin(admin.ModelAdmin):
    pass
