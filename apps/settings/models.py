from django.db import models


class CompanySetting(models.Model):
    company_name = models.CharField(max_length=200, default='Prime Lands Ltd')
    tagline = models.CharField(max_length=200, default='Your Trusted Real Estate Partner')
    email = models.EmailField(default='info@primelands.com')
    phone = models.CharField(max_length=20, default='+254 700 000 000')
    address = models.TextField(default='99 Westlands Rd, Nairobi, Kenya')
    logo = models.ImageField(upload_to='settings/', blank=True)
    favicon = models.ImageField(upload_to='settings/', blank=True)
    google_maps_api_key = models.CharField(max_length=200, blank=True)
    about_text = models.TextField(blank=True)
    mission_text = models.TextField(blank=True)
    vision_text = models.TextField(blank=True)
    social_facebook = models.URLField(blank=True)
    social_twitter = models.URLField(blank=True)
    social_instagram = models.URLField(blank=True)
    social_linkedin = models.URLField(blank=True)
    deposit_percentage_default = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    installment_months_default = models.IntegerField(default=60)
    interest_rate_default = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    receipt_prefix = models.CharField(max_length=10, default='RCP')
    currency_symbol = models.CharField(max_length=10, default='KSh')
    mpesa_callback_url = models.CharField(max_length=500, blank=True,
                                          default='https://9cc3-102-205-50-218.ngrok-free.app/payments/mpesa/callback/',
                                          help_text='Public URL for M-Pesa STK Push callback')
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5,
                                                help_text='Platform commission percentage on each sale')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Setting'
        verbose_name_plural = 'Company Settings'

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        # Ensure only one settings record exists
        if not self.pk and CompanySetting.objects.exists():
            return
        super().save(*args, **kwargs)


class PageContent(models.Model):
    PAGE_CHOICES = [
        ('about', 'About Us'),
        ('faq', 'FAQs'),
        ('terms', 'Terms & Conditions'),
        ('privacy', 'Privacy Policy'),
        ('hire_purchase', 'Hire Purchase'),
    ]

    page = models.CharField(max_length=30, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_page_display()
