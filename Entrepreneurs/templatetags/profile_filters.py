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