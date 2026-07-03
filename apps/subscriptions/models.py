from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class SubscriptionPlan(models.Model):
    PLAN_TYPE = [
        ('fixed', 'Fixed Monthly Fee'),
        ('percentage', 'Percentage of Sales'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE, default='fixed')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Monthly price (for fixed plans)")
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                help_text="Platform commission % per sale (for percentage plans)")
    duration_days = models.IntegerField(default=30, help_text="Duration in days")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        if self.plan_type == 'fixed':
            return f"{self.name} - KSh {self.price}/month"
        return f"{self.name} - {self.commission_percentage}%/sale"


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-end_date']

    def __str__(self):
        return f"{self.user.get_full_name_or_username()} - {self.plan}"

    @property
    def days_remaining(self):
        remaining = (self.end_date - timezone.now().date()).days
        return max(0, remaining)

    @property
    def is_expired(self):
        return self.end_date < timezone.now().date()

    @property
    def is_percentage_plan(self):
        return self.plan and self.plan.plan_type == 'percentage'

    def renew(self):
        new_start = self.end_date
        new_end = new_start + timezone.timedelta(days=self.plan.duration_days if self.plan else 30)
        return Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=new_start,
            end_date=new_end,
            is_active=True,
        )


class SubscriptionPayment(models.Model):
    PAYMENT_METHOD = [
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='mpesa')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    transaction_ref = models.CharField(max_length=200, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    payment_date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='subscription_confirmations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Sub Payment: {self.user} - {self.amount}"
