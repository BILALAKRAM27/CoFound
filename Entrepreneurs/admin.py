from django.contrib import admin
from .models import (
    User, Industry, EntrepreneurProfile, Startup, StartupDocument, Review, CollaborationRequest, Message, Notification, Favorite, ActivityLog, Post, PostMedia, Comment, Meeting
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at', 'last_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active', 'created_at')
    ordering = ('-created_at',)

@admin.register(EntrepreneurProfile)
class EntrepreneurProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'company_name', 'company_stage', 'funding_need', 'team_size', 'created_at')
    search_fields = ('user__email', 'company_name')
    list_filter = ('company_stage', 'funding_need', 'team_size')

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'entrepreneur', 'industry', 'funding_goal', 'created_at')
    search_fields = ('name', 'entrepreneur__email')
    list_filter = ('industry',)

@admin.register(StartupDocument)
class StartupDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'startup', 'title', 'file_name', 'uploaded_at')
    search_fields = ('startup__name', 'title', 'file_name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'entrepreneur', 'rating', 'created_at')
    search_fields = ('reviewer__email', 'entrepreneur__email')
    list_filter = ('rating',)

@admin.register(CollaborationRequest)
class CollaborationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor', 'entrepreneur', 'status', 'created_at')
    search_fields = ('investor__email', 'entrepreneur__email')
    list_filter = ('status',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'content', 'timestamp', 'is_read', 'message_type')
    search_fields = ('sender__email', 'receiver__email', 'content')
    list_filter = ('is_read', 'message_type', 'timestamp')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'sender', 'notification_type', 'title', 'is_read', 'created_at')
    search_fields = ('user__email', 'sender__email', 'title')
    list_filter = ('notification_type', 'is_read', 'created_at')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'target_user', 'created_at')
    search_fields = ('user__email', 'target_user__email')

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'timestamp')
    search_fields = ('user__email', 'action')
    list_filter = ('action', 'timestamp')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content', 'created_at', 'updated_at')
    search_fields = ('author__email', 'content')
    list_filter = ('created_at',)

@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'media_type', 'file_name', 'uploaded_at')
    search_fields = ('post__author__email', 'file_name')
    list_filter = ('media_type',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'content', 'created_at')
    search_fields = ('post__author__email', 'author__email', 'content')
    list_filter = ('created_at',)

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('id', 'organizer', 'participant', 'title', 'date', 'time', 'status', 'meeting_type')
    search_fields = ('organizer__email', 'participant__email', 'title')
    list_filter = ('status', 'meeting_type', 'date')

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
