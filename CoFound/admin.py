from django.contrib import admin
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site

# Register allauth models
from allauth.socialaccount.admin import SocialAppAdmin, SocialAccountAdmin, SocialTokenAdmin
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken

# Unregister and re-register to ensure proper registration
try:
    admin.site.unregister(SocialApp)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(SocialAccount)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(SocialToken)
except admin.sites.NotRegistered:
    pass

# Register allauth models
admin.site.register(SocialApp, SocialAppAdmin)
admin.site.register(SocialAccount, SocialAccountAdmin)
admin.site.register(SocialToken, SocialTokenAdmin)

# Ensure Site is registered
try:
    admin.site.unregister(Site)
except admin.sites.NotRegistered:
    pass

admin.site.register(Site, SiteAdmin)
