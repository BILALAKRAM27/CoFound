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
    path('user/<int:user_id>/network/', views.user_network, name='user_network'),
    path('messages/', views.messages_page, name='messages'),
    path('messages/settings/', views.message_settings, name='message_settings'),
    path('messages/search/', views.message_search, name='message_search'),
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

# Startup Management
urlpatterns += [
	path('startup/create/', views.create_startup, name='create_startup'),
]

# Notifications
urlpatterns += [
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('search/', views.search_users, name='search_users'),
    path('search/results/', views.search_results_page, name='search_results_page'),
    path('portfolio-analytics/', views.portfolio_analytics, name='portfolio_analytics'),
    path('notifications/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/unread-count/', views.get_unread_count, name='get_unread_count'),
    path('notifications/data/', views.get_notifications_data, name='get_notifications_data'),
]

# Meeting URLs
urlpatterns += [
    path('schedule-meeting/<int:user_id>/', views.schedule_meeting, name='schedule_meeting'),
    path('meetings/', views.meetings_list, name='meetings'),
    path('meetings/calendar/', views.meeting_calendar, name='meeting_calendar'),
    path('meetings/<int:meeting_id>/<str:action>/', views.respond_to_meeting, name='respond_to_meeting'),
    path('meetings/<int:meeting_id>/cancel/', views.cancel_meeting, name='cancel_meeting'),
]

# OAuth Authentication URLs
urlpatterns += [
    path('oauth/callback/', views.oauth_callback, name='oauth_callback'),
    path('role-selection/', views.role_selection, name='role_selection'),
]