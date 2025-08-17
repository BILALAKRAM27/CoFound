from django.urls import path
from . import views

app_name = 'investors'

urlpatterns = [
    path('register/', views.investor_register, name='register'),
    path('login/', views.investor_login, name='login'),
    path('logout/', views.investor_logout, name='logout'),
    path('dashboard/', views.investor_dashboard, name='dashboard'),
    path('profile/', views.investor_profile, name='profile'),
    path('upload-document/', views.upload_investment_document, name='upload_document'),
]