import base64
from django import template
from django.db.models import Q
from Entrepreneurs.models import CollaborationRequest, Favorite

register = template.Library()

@register.filter
def b64encode_blob(value):
    """
    Converts a BLOB (bytes) to a base64 string for embedding in <img> tags.
    Returns an empty string if value is None or not bytes.
    """
    if value and isinstance(value, (bytes, bytearray)):
        return base64.b64encode(value).decode('utf-8')
    return ''

@register.filter
def get_profile_image(user):
    try:
        if hasattr(user, 'entrepreneur_profile') and user.entrepreneur_profile.image:
            return user.entrepreneur_profile.image
        elif hasattr(user, 'investor_profile') and user.investor_profile.image:
            return user.investor_profile.image
    except Exception:
        pass
    return None

@register.filter
def can_connect(viewer, target):
    try:
        return bool(viewer.is_authenticated and viewer.id != target.id)
    except Exception:
        return False

@register.filter
def connection_status(viewer, target):
    try:
        if not viewer.is_authenticated or viewer.id == target.id:
            return 'self'
        # Following via Favorite (universal)
        if Favorite.objects.filter(user=viewer, target_user=target).exists():
            return 'accepted'
        # Legacy opposite-role connections
        req = CollaborationRequest.objects.filter(
            Q(investor=viewer, entrepreneur=target) | Q(investor=target, entrepreneur=viewer)
        ).order_by('-created_at').first()
        if req and req.status == 'accepted':
            return 'accepted'
        if req and req.status == 'pending':
            return 'pending'
        return 'none'
    except Exception:
        return 'none'

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get a dictionary value by key.
    Usage: {{ dictionary|get_item:key }}
    """
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None