from django.db import models
from apps.accounts.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('payment', 'Payment'),
        ('reminder', 'Reminder'),
        ('document', 'Document'),
        ('sale', 'Sale'),
        ('system', 'System'),
        ('support', 'Support'),
        ('customer', 'Customer'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient}"
