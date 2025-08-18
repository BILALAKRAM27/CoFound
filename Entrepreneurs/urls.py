from django.urls import path
from . import views

app_name = 'entrepreneurs'

urlpatterns = [
    path('dashboard/', views.entrepreneur_dashboard, name='dashboard'),
    path('profile/', views.entrepreneur_profile, name='profile'),
    path('create-post/', views.create_post, name='create_post'),
    path('like-post/<int:post_id>/', views.like_post, name='like_post'),
]

# Comment endpoints
urlpatterns += [
    path('add-comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('edit-comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
]