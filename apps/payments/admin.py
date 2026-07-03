from django.contrib import admin
from .models import Payment, MpesaTransaction

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'customer', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method']

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    pass
