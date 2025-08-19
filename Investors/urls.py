from django.urls import path
from . import views

app_name = 'investors'

urlpatterns = [
	path('register/', views.investor_register, name='register'),
	path('login/', views.investor_login, name='login'),
	path('logout/', views.investor_logout, name='logout'),
	path('dashboard/', views.investor_dashboard, name='dashboard'),
	path('profile/', views.investor_profile, name='profile'),
	path('profile/<int:user_id>/', views.investor_profile_detail, name='profile_detail'),
	path('create-post/', views.create_post, name='create_post'),
	path('like-post/<int:post_id>/', views.like_post, name='like_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/remove-media/<int:media_id>/', views.remove_post_media, name='remove_post_media'),
    path('posts/<int:post_id>/reorder-media/', views.reorder_post_media, name='reorder_post_media'),
    path('toggle-connect/<int:target_id>/', views.toggle_connection, name='toggle_connect'),
    path('my-network/', views.my_network, name='my_network'),
    path('network-data/', views.network_data, name='network_data'),
    path('messages/', views.messages_page, name='messages'),
    path('messages/settings/', views.message_settings, name='message_settings'),
    path('messages/search/', views.message_search, name='message_search'),
    path('messages/<int:user_id>/', views.get_messages, name='get_messages'),
]

# Comments
urlpatterns += [
	path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
	path('edit-comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
	path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]

# Saved posts
urlpatterns += [
	path('toggle-save/<int:post_id>/', views.toggle_save, name='toggle_save'),
	path('saved-posts/', views.saved_posts, name='saved_posts'),
]

# Discovery
urlpatterns += [
	path('find-startups/', views.find_startups, name='find_startups'),
	path('connect/<int:target_id>/', views.investor_connect, name='connect_startup'),
]