import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CoFound.settings')
django.setup()

from Entrepreneurs.models import Notification, Message

fixed = 0
skipped = 0
for n in Notification.objects.filter(notification_type='message'):
    try:
        # Only fix if related_object_id is a message ID (i.e., points to a Message)
        msg = Message.objects.get(id=n.related_object_id)
        if n.related_object_id != msg.sender.id:
            n.related_object_id = msg.sender.id
            n.related_object_type = 'user'
            n.save(update_fields=['related_object_id', 'related_object_type'])
            print(f"Fixed notification {n.id}: now points to user {msg.sender.id}")
            fixed += 1
        else:
            skipped += 1
    except Exception as e:
        print(f"Could not fix notification {n.id}: {e}")
        skipped += 1
print(f"Done. Fixed: {fixed}, Skipped: {skipped}")
