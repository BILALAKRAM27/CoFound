from django.urls import path
from . import views

app_name = 'entrepreneurs'

urlpatterns = [
    path('register/', views.entrepreneur_register, name='register'),
    path('login/', views.entrepreneur_login, name='login'),
    path('logout/', views.entrepreneur_logout, name='logout'),
    path('dashboard/', views.entrepreneur_dashboard, name='dashboard'),
    path('profile/', views.entrepreneur_profile, name='profile'),
    path('upload-document/', views.upload_startup_document, name='upload_document'),
]