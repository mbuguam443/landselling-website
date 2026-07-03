from django.db import models
from apps.projects.models import Project, ProjectPhase, Amenity
from django.utils import timezone


class Plot(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('blocked', 'Blocked'),
    ]

    plot_number = models.CharField(max_length=50)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='plots')
    phase = models.ForeignKey(ProjectPhase, on_delete=models.SET_NULL, null=True, blank=True, related_name='plots')
    size_sqm = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    deposit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20,
                                             help_text="Percentage required as deposit")
    max_installment_months = models.IntegerField(default=60)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                        help_text="Annual interest rate for installments (%)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    description = models.TextField(blank=True)
    coordinates = models.CharField(max_length=100, blank=True, help_text="Google Maps coordinates")
    amenities = models.ManyToManyField(Amenity, blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['project', 'plot_number']
        unique_together = ['project', 'plot_number']

    def __str__(self):
        return f"{self.project.name} - Plot {self.plot_number}"

    @property
    def deposit_amount(self):
        return self.price * self.deposit_percentage / 100

    @property
    def balance(self):
        return self.price - self.deposit_amount

    def monthly_installment(self, months=None):
        m = months or self.max_installment_months
        if m <= 0:
            return 0
        if self.interest_rate > 0:
            monthly_rate = self.interest_rate / 100 / 12
            if monthly_rate > 0:
                payment = self.balance * (monthly_rate * (1 + monthly_rate) ** m) / ((1 + monthly_rate) ** m - 1)
                return round(payment, 2)
        return round(self.balance / m, 2)


class PlotImage(models.Model):
    plot = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='plots/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.plot}"
