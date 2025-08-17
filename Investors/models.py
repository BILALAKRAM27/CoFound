from django.db import models
# Import the shared User & Industry from entrepreneurs app
from Entrepreneurs.models import User, Industry, Startup


class InvestorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="investor_profile",
        limit_choices_to={'role': 'investor'}
    )

    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(blank=True, null=True, unique=True)

    # Profile picture as BLOB
    image = models.BinaryField(editable=True,blank=True, null=True)

    # Preferences
    investment_interests = models.ManyToManyField(Industry, related_name='interested_investors', blank=True)
    min_investment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_investment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    preferred_stages = models.CharField(max_length=255, blank=True, help_text='Comma-separated stages')

    # Professional Info
    firm_name = models.CharField(max_length=255, blank=True, unique=True)
    position = models.CharField(max_length=100, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)

    # Social
    website = models.URLField(blank=True, null=True, unique=True)
    twitter_handle = models.CharField(max_length=50, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def image_base64(self):
        if self.image:
            import base64
            return base64.b64encode(self.image).decode('utf-8')
        return None

    @property
    def image_data(self):
        """Property to access image as base64 string for templates"""
        return self.image_base64()

    def __str__(self):
        return f"Investor Profile: {self.user.get_full_name() or self.user.email}"


class InvestorPortfolio(models.Model):
    # Keep portfolio summary distinct from profile (to avoid duplication)
    investor = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="portfolio",
        limit_choices_to={'role': 'investor'}
    )
    total_investments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    number_of_investments = models.PositiveIntegerField(default=0)
    notable_exits = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Portfolio of {self.investor.get_full_name() or self.investor.email}"


class InvestmentDocument(models.Model):
    investor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='investment_documents',
        limit_choices_to={'role': 'investor'}
    )
    title = models.CharField(max_length=255)

    # BLOB file storage for PDFs, contracts, etc.
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100, blank=True)  # e.g., "application/pdf"
    file_data = models.BinaryField(editable=True,blank=True, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def file_base64(self):
        if self.file_data:
            import base64
            return base64.b64encode(self.file_data).decode('utf-8')
        return None

    @property
    def file_data_display(self):
        """Property to access file data as base64 string for templates"""
        return self.file_base64()

    def __str__(self):
        return f"{self.title} by {self.investor}"
