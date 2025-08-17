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
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from Investors.views import index, home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),  # Landing page
    path('home/', home, name='home'),  # Common home page
    path('entrepreneur/', include('Entrepreneurs.urls', namespace='entrepreneurs')),
    path('investor/', include('Investors.urls', namespace='investors')),
]
