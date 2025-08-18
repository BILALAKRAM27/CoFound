from django.urls import path
from . import views

app_name = 'investors'

urlpatterns = [
    path('register/', views.investor_register, name='register'),
    path('login/', views.investor_login, name='login'),
    path('logout/', views.investor_logout, name='logout'),
    path('dashboard/', views.investor_dashboard, name='dashboard'),
    path('profile/', views.investor_profile, name='profile'),
    path('create-post/', views.create_post, name='create_post'),
    path('like-post/<int:post_id>/', views.like_post, name='like_post'),
]

urlpatterns += [
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
]