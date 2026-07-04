from django.contrib import admin
from .models import Payment, MpesaTransaction

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'customer', 'amount', 'payment_method', 'mpesa_code', 'status', 'payment_date']
    list_filter = ['status', 'payment_method']
    search_fields = ['receipt_number', 'mpesa_code', 'customer__name']

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ['payment', 'mpesa_receipt_number', 'phone_number', 'amount', 'status', 'transaction_date']
    list_filter = ['status', 'transaction_type']
    search_fields = ['mpesa_receipt_number', 'phone_number']
