from django.db import models
from apps.sales.models import Sale
from apps.customers.models import Customer


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('sale_agreement', 'Sale Agreement'),
        ('booking_form', 'Booking Form'),
        ('payment_receipt', 'Payment Receipt'),
        ('payment_statement', 'Payment Statement'),
        ('survey_map', 'Survey Map'),
        ('beacon_certificate', 'Beacon Certificate'),
        ('transfer_form', 'Transfer Form'),
        ('title_deed', 'Title Deed'),
        ('id_document', 'Identification Document'),
        ('passport_photo', 'Passport Photo'),
        ('proof_of_payment', 'Proof of Payment'),
        ('completion_certificate', 'Completion Certificate'),
        ('project_brochure', 'Project Brochure'),
        ('company_document', 'Company Document'),
        ('other', 'Other'),
    ]

    VISIBILITY_CHOICES = [
        ('customer', 'Customer Only'),
        ('staff', 'Staff Only'),
        ('both', 'Customer & Staff'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('replaced', 'Replaced'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='both')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    version = models.IntegerField(default=1)
    is_auto_generated = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.title}"
