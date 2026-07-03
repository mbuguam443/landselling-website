from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'Super Admin'
        ADMINISTRATOR = 'administrator', 'Administrator'
        FINANCE_OFFICER = 'finance_officer', 'Finance Officer'
        SALES_AGENT = 'sales_agent', 'Sales Agent'
        CUSTOMER_CARE = 'customer_care', 'Customer Care'
        CUSTOMER = 'customer', 'Customer'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)

    def is_staff_or_above(self):
        return self.role in [self.Role.SUPER_ADMIN, self.Role.ADMINISTRATOR,
                             self.Role.FINANCE_OFFICER, self.Role.SALES_AGENT,
                             self.Role.CUSTOMER_CARE]

    def is_admin_or_above(self):
        return self.role in [self.Role.SUPER_ADMIN, self.Role.ADMINISTRATOR]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
