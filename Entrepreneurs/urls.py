from django.urls import path
from . import views

app_name = 'entrepreneurs'

urlpatterns = [
    path('register/', views.entrepreneur_register, name='register'),
    path('login/', views.entrepreneur_login, name='login'),
    path('logout/', views.entrepreneur_logout, name='logout'),
	path('dashboard/', views.entrepreneur_dashboard, name='dashboard'),
	path('profile/', views.entrepreneur_profile, name='profile'),
	path('profile/<int:user_id>/', views.entrepreneur_profile_detail, name='profile_detail'),
	path('create-post/', views.create_post, name='create_post'),
	path('like-post/<int:post_id>/', views.like_post, name='like_post'),
]

# Comments
urlpatterns += [
	path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
	path('edit-comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
	path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]

# Discovery
urlpatterns += [
	path('find-investors/', views.find_investors, name='find_investors'),
	path('connect/<int:target_id>/', views.entrepreneur_connect, name='connect_investor'),
]