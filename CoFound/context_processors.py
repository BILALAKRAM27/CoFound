import base64

def user_profile_context(request):
    """
    Adds the user's profile image BLOB to the template context as user_profile_image_blob.
    Also adds unread notification count and debug info for troubleshooting.
    Adds sidebar counts for connections, posts, and views for both investors and entrepreneurs.
    """
    context = {}
    debug_info = {}

    if request.user.is_authenticated:
        try:
            # Get profile image
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
                
            # Get unread notification count
            try:
                from Entrepreneurs.models import Notification
                unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
                context['unread_notification_count'] = unread_count
                debug_info['unread_notifications'] = unread_count
            except Exception as e:
                context['unread_notification_count'] = 0
                debug_info['notification_error'] = str(e)

            # Sidebar counts
            sidebar_connections_count = 0
            sidebar_posts_count = 0
            sidebar_profile_views = 0
            try:
                if request.user.role == 'investor':
                    from Entrepreneurs.models import Favorite, CollaborationRequest
                    favorites_count = Favorite.objects.filter(user=request.user).count()
                    accepted_requests = CollaborationRequest.objects.filter(
                        investor=request.user, status='accepted'
                    ).count()
                    sidebar_connections_count = favorites_count + accepted_requests
                    sidebar_posts_count = request.user.posts.count() if hasattr(request.user, 'posts') else 0
                    sidebar_profile_views = profile.profile_views if profile else 0
                elif request.user.role == 'entrepreneur':
                    from Entrepreneurs.models import Favorite, CollaborationRequest
                    favorites_count = Favorite.objects.filter(user=request.user).count()
                    accepted_requests = CollaborationRequest.objects.filter(
                        entrepreneur=request.user, status='accepted'
                    ).count()
                    sidebar_connections_count = favorites_count + accepted_requests
                    sidebar_posts_count = request.user.posts.count() if hasattr(request.user, 'posts') else 0
                    sidebar_profile_views = profile.profile_views if profile else 0
            except Exception as e:
                debug_info['sidebar_counts_error'] = str(e)
            context['sidebar_connections_count'] = sidebar_connections_count
            context['sidebar_posts_count'] = sidebar_posts_count
            context['sidebar_profile_views'] = sidebar_profile_views

        except Exception as e:
            context['user_profile_image_blob'] = None
            context['unread_notification_count'] = 0
            context['sidebar_connections_count'] = 0
            context['sidebar_posts_count'] = 0
            context['sidebar_profile_views'] = 0
            debug_info['profile_image_error'] = str(e)
    else:
        context['user_profile_image_blob'] = None
        context['unread_notification_count'] = 0
        context['sidebar_connections_count'] = 0
        context['sidebar_posts_count'] = 0
        context['sidebar_profile_views'] = 0
        debug_info['profile_image_type'] = 'Not authenticated'
        debug_info['profile_image_size'] = 0

    # Add debug info to context (remove/comment out in production)
    context['profile_image_debug'] = debug_info
    return context