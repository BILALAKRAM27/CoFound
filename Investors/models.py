from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from Entrepreneurs.models import User
from decimal import Decimal

# Choice constants for InvestorProfile
INVESTMENT_STAGES = [
    ('not_specified', 'Not Specified'),
    ('seed', 'Seed'),
    ('series_a', 'Series A'),
    ('series_b', 'Series B'),
    ('series_c', 'Series C'),
    ('growth', 'Growth'),
    ('late_stage', 'Late Stage')
]

INVESTMENT_SIZES = [
    ('not_specified', 'Not Specified'),
    ('0-50k', '$0 - $50K'),
    ('50k-500k', '$50K - $500K'),
    ('500k-5m', '$500K - $5M'),
    ('5m-50m', '$5M - $50M'),
    ('50m+', '$50M+')
]

# Industry choices for both entrepreneurs and investors
INDUSTRY_CHOICES = [
    ('ai', 'Artificial Intelligence (AI)'),
    ('fintech', 'Fintech'),
    ('healthtech', 'Healthtech'),
    ('enterprise_saas', 'Enterprise AI SaaS'),
    ('logistics', 'Logistics & Supply Chain Tech'),
    ('quantum', 'Quantum Computing'),
    ('insurtech', 'InsurTech'),
    ('spacetech', 'SpaceTech'),
    ('creator_tools', 'Creator Economy Tools'),
    ('cleantech', 'CleanTech & Green Energy'),
]



# -----------------------------
# Investors domain
# -----------------------------


class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='investor_profile')
    firm_name = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    investment_stage = models.CharField(max_length=50, choices=INVESTMENT_STAGES, default='not_specified')
    investment_size = models.CharField(max_length=50, choices=INVESTMENT_SIZES, default='not_specified')
    preferred_industries = models.CharField(max_length=500, blank=True, choices=INDUSTRY_CHOICES)
    portfolio_companies = models.TextField(blank=True)
    notable_exits = models.TextField(blank=True)
    image = models.BinaryField(editable=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Investor Profile"


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


class FundingRound(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]
    startup = models.ForeignKey(
        'Entrepreneurs.Startup',
        on_delete=models.CASCADE,
        related_name='funding_rounds'
    )
    round_name = models.CharField(max_length=255)
    target_goal = models.DecimalField(max_digits=12, decimal_places=2)
    equity_offered = models.DecimalField(max_digits=5, decimal_places=2, help_text='Total equity offered (%)')
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_committed(self):
        return sum(ic.amount for ic in self.investments.all())

    def is_successful(self):
        return self.total_committed() >= self.target_goal

    def __str__(self):
        return f"{self.round_name} for {self.startup.name}"

class InvestmentCommitment(models.Model):
    funding_round = models.ForeignKey(FundingRound, on_delete=models.CASCADE, related_name='investments')
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investment_commitments', limit_choices_to={'role': 'investor'})
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    committed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('funding_round', 'investor')

    @property
    def equity_share(self):
        # Proportional equity based on amount committed
        if self.funding_round.target_goal > 0:
            # Ensure amount is a Decimal
            try:
                amount = Decimal(str(self.amount)) if not isinstance(self.amount, Decimal) else self.amount
                return (amount / self.funding_round.target_goal) * self.funding_round.equity_offered
            except (ValueError, TypeError, AttributeError):
                return 0
        return 0

    def __str__(self):
        return f"{self.investor.get_full_name()} committed ${self.amount} to {self.funding_round.round_name}"
