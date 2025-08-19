from django.urls import path
from . import views
from .views import get_messages

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
    path('my-posts/', views.my_posts, name='my_posts'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/remove-media/<int:media_id>/', views.remove_post_media, name='remove_post_media'),
    path('posts/<int:post_id>/reorder-media/', views.reorder_post_media, name='reorder_post_media'),
    path('toggle-connect/<int:target_id>/', views.toggle_connection, name='toggle_connect'),
    path('messages/<int:user_id>/', get_messages, name='get_messages'),
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