from django.contrib import admin
from .models import Sale, InstallmentSchedule, Reservation

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['customer', 'plot', 'selling_price', 'status', 'sale_date']
    list_filter = ['status']

@admin.register(InstallmentSchedule)
class InstallmentScheduleAdmin(admin.ModelAdmin):
    pass

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    pass
