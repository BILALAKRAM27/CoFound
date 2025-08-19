import base64
from django import template

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
