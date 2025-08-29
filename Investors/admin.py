from django.contrib import admin
from .models import (
    InvestorProfile, InvestorPortfolio, InvestmentDocument, FundingRound, InvestmentCommitment
)
from Entrepreneurs.models import Notification

@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'firm_name', 'investment_stage', 'investment_size', 'created_at')
    search_fields = ('user__email', 'firm_name')
    list_filter = ('investment_stage', 'investment_size')

@admin.register(InvestorPortfolio)
class InvestorPortfolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor', 'total_investments', 'number_of_investments', 'updated_at')
    search_fields = ('investor__email',)

@admin.register(InvestmentDocument)
class InvestmentDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor', 'title', 'file_name', 'uploaded_at')
    search_fields = ('investor__email', 'title', 'file_name')

@admin.register(FundingRound)
class FundingRoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'startup', 'round_name', 'target_goal', 'equity_offered', 'deadline', 'status', 'created_at')
    search_fields = ('startup__name', 'round_name')
    list_filter = ('status', 'deadline', 'created_at')

@admin.register(InvestmentCommitment)
class InvestmentCommitmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'funding_round', 'investor', 'amount', 'committed_at')
    search_fields = ('funding_round__round_name', 'investor__email')
    list_filter = ('committed_at',)

