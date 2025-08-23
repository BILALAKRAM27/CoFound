from django.contrib import admin
from .models import FundingRound, InvestmentCommitment
from Entrepreneurs.models import Notification

# Register your models here.

admin.site.register(FundingRound)
admin.site.register(InvestmentCommitment)
admin.site.register(Notification)
