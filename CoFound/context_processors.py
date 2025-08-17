import base64

def user_profile_context(request):
    """
    Adds the user's profile image BLOB to the template context as user_profile_image_blob.
    Also adds debug info for troubleshooting.
    """
    context = {}
    debug_info = {}

    if request.user.is_authenticated:
        try:
            if request.user.role == 'entrepreneur':
                profile = getattr(request.user, 'entrepreneur_profile', None)
            elif request.user.role == 'investor':
                profile = getattr(request.user, 'investor_profile', None)
            else:
                profile = None

            if profile and profile.image:
                context['user_profile_image_blob'] = profile.image
                debug_info['profile_image_type'] = str(type(profile.image))
                debug_info['profile_image_size'] = len(profile.image) if hasattr(profile.image, '__len__') else 'N/A'
            else:
                context['user_profile_image_blob'] = None
                debug_info['profile_image_type'] = 'None'
                debug_info['profile_image_size'] = 0
        except Exception as e:
            context['user_profile_image_blob'] = None
            debug_info['profile_image_error'] = str(e)
    else:
        context['user_profile_image_blob'] = None
        debug_info['profile_image_type'] = 'Not authenticated'
        debug_info['profile_image_size'] = 0

    # Add debug info to context (remove/comment out in production)
    context['profile_image_debug'] = debug_info
    return context