from django.http import HttpResponse
from django.conf import settings
import os
from pathlib import Path

def favicon_view(request):
    """
    Serve favicon.ico file
    This view handles the favicon request explicitly for ASGI servers like Daphne
    """
    favicon_path = settings.BASE_DIR / 'static' / 'favicon.ico'
    
    if favicon_path.exists():
        with open(favicon_path, 'rb') as f:
            content = f.read()
        return HttpResponse(content, content_type='image/x-icon')
    else:
        # Return a minimal favicon if file doesn't exist
        return HttpResponse(
            b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x20\x00\x68\x04\x00\x00\x16\x00\x00\x00',
            content_type='image/x-icon'
        )
