from django.contrib.auth import get_user_model
User = get_user_model()
from Entrepreneurs.models import Notification
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json


class NotificationService:
    """Service class for handling notifications"""
    
    @staticmethod
    def create_notification(recipient, notification_type, title, message, sender=None, 
                          related_object_id=None, related_object_type=None):
        """
        Create a notification and send real-time update
        
        Args:
            recipient: User receiving the notification
            notification_type: Type of notification (follow, post, like, etc.)
            title: Notification title
            message: Notification message
            sender: User who triggered the notification (optional)
            related_object_id: ID of related object (optional)
            related_object_type: Type of related object (optional)
        """
        with transaction.atomic():
            # Create the notification
            notification = Notification.objects.create(
                user=recipient,
                sender=sender,
                notification_type=notification_type,
                title=title,
                message=message,
                related_object_id=related_object_id,
                related_object_type=related_object_type
            )
            
            # Send real-time notification via WebSocket
            NotificationService.send_realtime_notification(recipient.id, notification)
            
            return notification
    
    @staticmethod
    def send_realtime_notification(user_id, notification):
        """Send real-time notification via WebSocket"""
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notifications_{user_id}",
                {
                    "type": "notification_message",
                    "notification": {
                        "id": notification.id,
                        "type": notification.notification_type,
                        "title": notification.title,
                        "message": notification.message,
                        "sender_name": notification.sender.get_full_name() if notification.sender else None,
                        "time_ago": notification.time_ago,
                        "related_object_id": notification.related_object_id if notification.related_object_id else (notification.sender.id if notification.notification_type == 'follow' and notification.sender else None),
                        "related_object_type": notification.related_object_type,
                    }
                }
            )
        except Exception as e:
            # Log error but don't fail the notification creation
            print(f"Error sending real-time notification: {e}")
    
    @staticmethod
    def mark_as_read(notification_id, user):
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user"""
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    
    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for a user"""
        return Notification.objects.filter(user=user, is_read=False).count()
    
    @staticmethod
    def get_user_notifications(user, limit=50):
        """Get user's notifications with pagination"""
        return Notification.objects.filter(user=user)[:limit]


# Convenience functions for specific notification types
def notify_follow(follower, followed_user):
    """Notify when someone follows a user"""
    NotificationService.create_notification(
        recipient=followed_user,
        sender=follower,
        notification_type='follow',
        title='New Follower',
        message=f'{follower.get_full_name() or follower.email} started following you',
        related_object_id=follower.id,  # Fix: set to follower's id for redirect
        related_object_type='user'
    )

def notify_post_created(post):
    """Notify followers when a new post is created"""
    from Entrepreneurs.models import Favorite
    
    # Get all users who follow the post author
    followers = Favorite.objects.filter(target_user=post.author).values_list('user', flat=True)
    
    for follower_id in followers:
        follower = post.author.__class__.objects.get(id=follower_id)
        NotificationService.create_notification(
            recipient=follower,
            sender=post.author,
            notification_type='post',
            title='New Post',
            message=f'{post.author.get_full_name() or post.author.email} created a new post',
            related_object_id=post.id,
            related_object_type='post'
        )

def notify_like(post, liker):
    """Notify post author when someone likes their post"""
    if liker != post.author:  # Don't notify self-likes
        NotificationService.create_notification(
            recipient=post.author,
            sender=liker,
            notification_type='like',
            title='New Like',
            message=f'{liker.get_full_name() or liker.email} liked your post',
            related_object_id=post.id,
            related_object_type='post'
        )

def notify_comment(post, commenter):
    """Notify post author when someone comments on their post"""
    if commenter != post.author:  # Don't notify self-comments
        NotificationService.create_notification(
            recipient=post.author,
            sender=commenter,
            notification_type='comment',
            title='New Comment',
            message=f'{commenter.get_full_name() or commenter.email} commented on your post',
            related_object_id=post.id,
            related_object_type='post'
        )

def notify_startup_created(startup):
    """Notify when a startup is created"""
    from Entrepreneurs.models import User
    
    # Notify all investors about new startup
    investors = User.objects.filter(role='investor')
    
    for investor in investors:
        NotificationService.create_notification(
            recipient=investor,
            sender=startup.entrepreneur,
            notification_type='startup',
            title='New Startup',
            message=f'{startup.entrepreneur.get_full_name() or startup.entrepreneur.email} created a new startup: {startup.name}',
            related_object_id=startup.id,
            related_object_type='startup'
        )

def notify_funding_round_created(funding_round):
    """Notify when a funding round is created"""
    from Entrepreneurs.models import User
    
    # Notify all investors about new funding round
    investors = User.objects.filter(role='investor')
    
    for investor in investors:
        NotificationService.create_notification(
            recipient=investor,
            sender=funding_round.startup.entrepreneur,
            notification_type='funding_round',
            title='New Funding Round',
            message=f'{funding_round.startup.name} created a new funding round: {funding_round.round_name}',
            related_object_id=funding_round.id,
            related_object_type='funding_round'
        )

def notify_investment_committed(funding_round, investor, amount):
    """Notify startup when someone commits to their funding round"""
    NotificationService.create_notification(
        recipient=funding_round.startup.entrepreneur,
        sender=investor,
        notification_type='investment',
        title='New Investment Commitment',
        message=f'{investor.get_full_name() or investor.email} committed ${amount:,.0f} to your funding round',
        related_object_id=funding_round.id,
        related_object_type='funding_round'
    )

def notify_message_received(message):
    """Notify user when they receive a new message"""
    NotificationService.create_notification(
        recipient=message.receiver,
        sender=message.sender,
        notification_type='message',
        title='New Message',
        message=f'{message.sender.get_full_name() or message.sender.email} sent you a message',
        related_object_id=message.id,
        related_object_type='message'
    )
