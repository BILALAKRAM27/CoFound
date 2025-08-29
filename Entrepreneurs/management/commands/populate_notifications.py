from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from Entrepreneurs.models import Notification, ActivityLog
import random
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate notifications and activity logs for all users'

    def handle(self, *args, **options):
        self.stdout.write('Populating notifications and activity logs...')
        
        # Get all users
        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        notifications_created = 0
        activity_logs_created = 0
        
        # Sample notification content
        notification_templates = {
            'follow': {
                'title': 'New Follower',
                'message': '{sender} started following you'
            },
            'post': {
                'title': 'New Post',
                'message': '{sender} posted: {content}'
            },
            'like': {
                'title': 'New Like',
                'message': '{sender} liked your post'
            },
            'comment': {
                'title': 'New Comment',
                'message': '{sender} commented on your post'
            },
            'startup': {
                'title': 'Startup Update',
                'message': '{sender} updated their startup profile'
            },
            'funding_round': {
                'title': 'New Funding Round',
                'message': '{sender} created a new funding round'
            },
            'investment': {
                'title': 'New Investment',
                'message': '{sender} made an investment commitment'
            },
            'message': {
                'title': 'New Message',
                'message': '{sender} sent you a message'
            }
        }
        
        # Sample post content for notifications
        sample_post_content = [
            "Just launched our MVP!",
            "Excited to announce our funding round!",
            "Looking for talented developers to join our team.",
            "Our platform just hit 10,000 users!",
            "Working on some exciting new features!"
        ]
        
        # Create notifications for various activities
        for user in users:
            # Create 5-15 notifications per user
            num_notifications = random.randint(5, 15)
            
            for i in range(num_notifications):
                # Random notification type
                notification_type = random.choice(list(notification_templates.keys()))
                
                # Random sender (excluding self)
                potential_senders = [u for u in users if u != user]
                if potential_senders:
                    sender = random.choice(potential_senders)
                    
                    # Get template
                    template = notification_templates[notification_type]
                    
                    # Format message
                    if notification_type == 'post':
                        content = random.choice(sample_post_content)
                        message = template['message'].format(sender=sender.get_full_name(), content=content)
                    else:
                        message = template['message'].format(sender=sender.get_full_name())
                    
                    # Random timestamp within last 30 days
                    timestamp = timezone.now() - timedelta(days=random.randint(0, 30))
                    
                    # Random read status (mostly unread)
                    is_read = random.random() < 0.3  # 30% chance of being read
                    
                    # Create notification
                    Notification.objects.create(
                        user=user,
                        sender=sender,
                        notification_type=notification_type,
                        title=template['title'],
                        message=message,
                        is_read=is_read,
                        created_at=timestamp
                    )
                    notifications_created += 1
        
        # Create activity logs
        activity_templates = {
            'login': 'User logged into the platform',
            'view_profile': 'User viewed profile of {target}',
            'send_request': 'User sent collaboration request to {target}',
            'accept_request': 'User accepted collaboration request from {target}',
            'send_message': 'User sent message to {target}'
        }
        
        for user in users:
            # Create 8-20 activity logs per user
            num_activities = random.randint(8, 20)
            
            for i in range(num_activities):
                # Random activity type
                activity_type = random.choice(list(activity_templates.keys()))
                
                # Random timestamp within last 30 days
                timestamp = timezone.now() - timedelta(days=random.randint(0, 30))
                
                # Format details
                if activity_type in ['view_profile', 'send_request', 'accept_request', 'send_message']:
                    # Need a target user
                    potential_targets = [u for u in users if u != user]
                    if potential_targets:
                        target = random.choice(potential_targets)
                        details = activity_templates[activity_type].format(target=target.get_full_name())
                    else:
                        details = activity_templates[activity_type].format(target='another user')
                else:
                    details = activity_templates[activity_type]
                
                # Create activity log
                ActivityLog.objects.create(
                    user=user,
                    action=activity_type,
                    details=details,
                    timestamp=timestamp
                )
                activity_logs_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {notifications_created} notifications and {activity_logs_created} activity logs!'
            )
        )
        
        # Display statistics
        total_notifications = Notification.objects.count()
        unread_notifications = Notification.objects.filter(is_read=False).count()
        read_notifications = Notification.objects.filter(is_read=True).count()
        total_activity_logs = ActivityLog.objects.count()
        
        self.stdout.write(f'Total notifications: {total_notifications}')
        self.stdout.write(f'Read notifications: {read_notifications}')
        self.stdout.write(f'Unread notifications: {unread_notifications}')
        self.stdout.write(f'Total activity logs: {total_activity_logs}')
        
        # Show notification type breakdown
        self.stdout.write('\nNotification breakdown by type:')
        for notification_type in notification_templates.keys():
            count = Notification.objects.filter(notification_type=notification_type).count()
            self.stdout.write(f'  {notification_type}: {count}')
        
        # Show activity log breakdown
        self.stdout.write('\nActivity log breakdown by type:')
        for activity_type in activity_templates.keys():
            count = ActivityLog.objects.filter(action=activity_type).count()
            self.stdout.write(f'  {activity_type}: {count}')
        
        # Show some sample notifications
        self.stdout.write('\nSample notifications:')
        for notification in Notification.objects.all()[:5]:
            self.stdout.write(
                f'  {notification.user.get_full_name()}: {notification.title} - '
                f'{notification.message[:50]}{"..." if len(notification.message) > 50 else ""} '
                f'({"read" if notification.is_read else "unread"})'
            )
        
        # Show some sample activity logs
        self.stdout.write('\nSample activity logs:')
        for activity in ActivityLog.objects.all()[:5]:
            self.stdout.write(
                f'  {activity.user.get_full_name()}: {activity.action} - '
                f'{activity.details[:50]}{"..." if len(activity.details) > 50 else ""}'
            )
