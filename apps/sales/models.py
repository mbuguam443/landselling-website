from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.customers.models import Customer
from apps.plots.models import Plot


class Sale(models.Model):
    SALE_STATUS = [
        ('reservation', 'Reservation'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('cancelled', 'Cancelled'),
        ('transferred', 'Transferred'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales')
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='sales')
    sales_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_made')
    sale_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=SALE_STATUS, default='reservation')
    selling_price = models.DecimalField(max_digits=15, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    deposit_paid = models.BooleanField(default=False)
    installment_months = models.IntegerField(default=60)
    monthly_installment = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grace_period_days = models.IntegerField(default=0)
    penalty_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                        help_text="Daily penalty rate (%)")
    commission_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                            help_text='Platform commission for this sale')
    commission_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    reservation_date = models.DateField(null=True, blank=True)
    reservation_expiry = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.name} - {self.plot}"

    @property
    def total_paid(self):
        return self.payments.filter(status='confirmed').aggregate(
            total=models.Sum('amount'))['total'] or 0

    @property
    def balance(self):
        return self.selling_price - self.total_paid

    @property
    def progress_percent(self):
        if self.selling_price == 0:
            return 0
        return min(100, int(self.total_paid / self.selling_price * 100))

    @property
    def next_due_date(self):
        upcoming = self.schedule.filter(status__in=['pending', 'partially_paid']).order_by('due_date').first()
        if upcoming:
            return upcoming.due_date
        return None

    @property
    def overdue_count(self):
        return self.schedule.filter(status='overdue').count()

    @property
    def overdue_amount(self):
        from django.db.models import Sum
        return self.schedule.filter(status='overdue').aggregate(
            total=Sum(models.F('amount') - models.F('amount_paid'))
        )['total'] or 0

    def generate_installment_schedule(self):
        self.schedule.all().delete()
        balance = self.selling_price - self.deposit_amount
        monthly = balance / self.installment_months if self.installment_months > 0 else 0
        from dateutil.relativedelta import relativedelta
        start_date = self.sale_date
        for i in range(self.installment_months):
            due = start_date + relativedelta(months=i + 1)
            InstallmentSchedule.objects.create(
                sale=self,
                installment_number=i + 1,
                due_date=due,
                amount=round(monthly, 2),
            )

    def save(self, *args, **kwargs):
        is_new = not self.pk
        if is_new and not self.monthly_installment and self.installment_months > 0:
            balance = self.selling_price - self.deposit_amount
            self.monthly_installment = round(balance / self.installment_months, 2) if self.installment_months > 0 else 0
        super().save(*args, **kwargs)
        if is_new and self.installment_months > 0:
            self.generate_installment_schedule()

    def calculate_commission(self):
        if self.commission_amount > 0:
            return self.commission_amount
        from apps.settings.models import CompanySetting
        from apps.subscriptions.models import Subscription
        from django.utils import timezone
        # Check if sales agent has an active percentage-based subscription
        if self.sales_agent:
            active_percentage_sub = Subscription.objects.filter(
                user=self.sales_agent,
                is_active=True,
                end_date__gte=timezone.now().date(),
                plan__plan_type='percentage',
                plan__commission_percentage__gt=0,
            ).first()
            if active_percentage_sub:
                pct = active_percentage_sub.plan.commission_percentage
                return round((self.selling_price * pct) / 100, 2)
        # Fall back to company default
        setting = CompanySetting.objects.first()
        pct = setting.commission_percentage if setting else 5
        amount = (self.selling_price * pct) / 100
        return round(amount, 2)

    def mark_commission_paid(self):
        if not self.commission_amount:
            self.commission_amount = self.calculate_commission()
        self.commission_paid = True
        self.save()


class InstallmentSchedule(models.Model):
    INSTALLMENT_STATUS = [
        ('pending', 'Pending'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('missed', 'Missed'),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='schedule')
    installment_number = models.IntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=INSTALLMENT_STATUS, default='pending')
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['sale', 'installment_number']

    def __str__(self):
        return f"{self.sale} - Installment #{self.installment_number}"

    @property
    def remaining(self):
        return self.amount - self.amount_paid

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.status in ('paid', 'cancelled'):
            return False
        return self.due_date < timezone.now().date()

    def update_status(self):
        if self.amount_paid >= self.amount:
            self.status = 'paid'
            self.paid = True
            self.paid_date = self.paid_date or timezone.now().date()
        elif self.amount_paid > 0:
            self.status = 'partially_paid'
            self.paid = False
        elif self.is_overdue:
            self.status = 'overdue'
            self.paid = False
        else:
            self.status = 'pending'
            self.paid = False


class Reservation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reservations')
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='reservations')
    reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reservation_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('converted', 'Converted'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], default='active')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-reservation_date']

    def __str__(self):
        return f"Reservation: {self.customer} - {self.plot}"
