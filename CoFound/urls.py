"""
URL configuration for CoFound project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Investors.views import index, home
from CoFound.views import favicon_view, about_view, contact_view, privacy_view, terms_view, cookies_view, security_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', favicon_view, name='favicon'),  # Explicit favicon handling
    path('', index, name='index'),  # Landing page
    path('home/', home, name='home'),  # Common home page
    
    # General Pages
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    path('privacy/', privacy_view, name='privacy'),
    path('terms/', terms_view, name='terms'),
    path('cookies/', cookies_view, name='cookies'),
    path('security/', security_view, name='security'),
    
    # OAuth Authentication URLs
    path('accounts/', include('allauth.urls')),
    
    path('entrepreneur/', include('Entrepreneurs.urls', namespace='entrepreneurs')),
    path('investor/', include('Investors.urls', namespace='investors')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
