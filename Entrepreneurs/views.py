
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import User, EntrepreneurProfile, Startup
from .forms import EntrepreneurRegistrationForm, EntrepreneurProfileForm, StartupForm
from django.http import JsonResponse
from .forms import PostForm
from .models import Post, PostMedia
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponseForbidden
from .models import Post, Comment, CollaborationRequest, EntrepreneurProfile, Favorite
from .forms import CommentForm
from django.shortcuts import get_object_or_404
import base64
from Investors.models import InvestorProfile
from django.db.models import Q
from django.db import transaction
from .models import Message, MessageSerializer
from .forms import MessageForm
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth.decorators import login_required

# --- Django Channels Consumer for Messaging (placeholder, to be moved to consumers.py) ---


def entrepreneur_register(request):
    if request.method == 'POST':
        form = EntrepreneurRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'entrepreneur'
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create a basic profile with default values
            profile = EntrepreneurProfile.objects.create(
                user=user,
                company_stage='idea',
                team_size='1',
                funding_raised='no_funding'
            )
            
            messages.success(request, 'Registration successful! Please log in to continue.')
            return redirect('entrepreneurs:login')  # Redirect to login page instead of auto-login
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = EntrepreneurRegistrationForm()
    
    return render(request, 'Entrepreneurs/Entrepreneur_register.html', {'form': form})


def entrepreneur_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'Entrepreneurs/Entrepreneur_login.html')
        
        user = authenticate(request, email=email, password=password)
        if user is not None and user.role == 'entrepreneur':
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('home')  # Redirect to base.html (common home)
        else:
            messages.error(request, 'Invalid credentials or not an entrepreneur.')
    
    return render(request, 'Entrepreneurs/Entrepreneur_login.html')


def entrepreneur_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')  # Redirect to landing page


@login_required
def entrepreneur_dashboard(request):
    if request.user.role != 'entrepreneur':
        messages.error(request, 'Access denied. You are not an entrepreneur.')
        return redirect('entrepreneurs:login')
        
    profile = EntrepreneurProfile.objects.get_or_create(user=request.user)[0]
    context = {
        'profile': profile,
    }
    return render(request, 'Entrepreneurs/dashboard.html', context)


@login_required
def entrepreneur_profile(request):
    if request.user.role != 'entrepreneur':
        messages.error(request, 'Access denied. You are not an entrepreneur.')
        return redirect('entrepreneurs:login')
    profile = EntrepreneurProfile.objects.get_or_create(user=request.user)[0]
    if request.method == 'POST':
        form = EntrepreneurProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            image_file = request.FILES.get('image_upload')
            if image_file:
                profile.image = image_file.read()
            profile.save()
            form.save_m2m()
            messages.success(request, 'Profile updated successfully!')
            return redirect('entrepreneurs:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = EntrepreneurProfileForm(instance=profile, user=request.user)
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'Entrepreneurs/profile.html', context)


@login_required
def upload_startup_document(request):
    """Handle startup document uploads"""
    if request.user.role != 'entrepreneur':
        messages.error(request, 'Access denied. You are not an entrepreneur.')
        return redirect('entrepreneurs:login')
    
    if request.method == 'POST':
        form = StartupDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the startup (assuming one startup per entrepreneur for now)
            startup = Startup.objects.filter(entrepreneur=request.user).first()
            if not startup:
                messages.error(request, 'Please create a startup first before uploading documents.')
                return redirect('entrepreneurs:profile')
            
            document = form.save(commit=False)
            document.startup = startup
            
            # Handle file upload and convert to BLOB
            if 'file' in request.FILES:
                file_obj = request.FILES['file']
                document.file_name = file_obj.name
                document.file_type = file_obj.content_type
                document.file_data = file_obj.read()
                document.save()
                messages.success(request, 'Document uploaded successfully!')
            else:
                messages.error(request, 'No file was uploaded.')
            
            return redirect('entrepreneurs:profile')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    return redirect('entrepreneurs:profile')


@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        images = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')
        documents = request.FILES.getlist('documents')
        if not content and not images and not videos and not documents:
            return JsonResponse({'success': False, 'errors': {'general': ['Please provide some content or media for your post.']}})
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                # Only save each file once
                for image in images:
                    PostMedia.objects.create(post=post, media_type='image', file_name=image.name, file_type=image.content_type, file_data=image.read(), file_size=image.size)
                for video in videos:
                    PostMedia.objects.create(post=post, media_type='video', file_name=video.name, file_type=video.content_type, file_data=video.read(), file_size=video.size)
                for document in documents:
                    PostMedia.objects.create(post=post, media_type='document', file_name=document.name, file_type=document.content_type, file_data=document.read(), file_size=document.size)
                
                # Send notification to followers
                from Investors.services import notify_post_created
                notify_post_created(post)
                
                messages.success(request, 'Post created successfully!')
                return JsonResponse({'success': True, 'post_id': post.id})
            except Exception as e:
                return JsonResponse({'success': False, 'errors': {'general': [f'Error creating post: {str(e)}']}})
        else:
            error_dict = {field: [str(error) for error in errors] for field, errors in form.errors.items()}
            return JsonResponse({'success': False, 'errors': error_dict})
    return JsonResponse({'success': False, 'errors': {'general': ['Invalid request method']}})

@login_required
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
            # Send notification to post author when someone likes their post
            if request.user != post.author:
                from Investors.services import notify_like
                notify_like(post, request.user)
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': post.likes.count()
        })
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Post not found'})


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

        # Send notification to post author when someone comments on their post
        if request.user != post.author:
            from Investors.services import notify_comment
            notify_comment(post, request.user)

        # Safely resolve and encode profile image
        image_bytes = None
        try:
            if hasattr(comment.author, 'entrepreneur_profile') and comment.author.entrepreneur_profile.image:
                image_bytes = comment.author.entrepreneur_profile.image
            elif hasattr(comment.author, 'investor_profile') and comment.author.investor_profile.image:
                image_bytes = comment.author.investor_profile.image
        except Exception:
            image_bytes = None
        author_image_b64 = base64.b64encode(image_bytes).decode('utf-8') if image_bytes else ''

        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'author_name': comment.author.get_full_name() or comment.author.email,
                'author_image': author_image_b64,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_POST
def edit_comment(request, comment_id):
	comment = get_object_or_404(Comment, id=comment_id)
	if comment.author != request.user:
		return HttpResponseForbidden('Not allowed')
	content = request.POST.get('content', '').strip()
	if not content:
		return JsonResponse({'success': False, 'errors': {'content': ['Content cannot be empty.']}}, status=400)
	comment.content = content
	comment.save(update_fields=['content', 'updated_at'])
	return JsonResponse({'success': True, 'comment': {'id': comment.id, 'content': comment.content}})

@login_required
@require_POST
def delete_comment(request, comment_id):
	comment = get_object_or_404(Comment, id=comment_id)
	if comment.author != request.user:
		return HttpResponseForbidden('Not allowed')
	comment.delete()
	return JsonResponse({'success': True})


@login_required
def find_investors(request):
    if request.user.role != 'entrepreneur':
        messages.error(request, 'Access denied.')
        return redirect('home')
    investors = InvestorProfile.objects.select_related('user').all()
    return render(request, 'Entrepreneurs/find_investors.html', { 'investors': investors })

@login_required
@require_POST
def entrepreneur_connect(request, target_id):
    if request.user.role != 'entrepreneur':
        return JsonResponse({'success': False, 'error': 'Access denied'})
    try:
        target = User.objects.get(id=target_id, role='investor')
        CollaborationRequest.objects.create(investor=target, entrepreneur=request.user, status='pending')
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def entrepreneur_profile_detail(request, user_id):
    from Investors.models import InvestorProfile
    from .models import EntrepreneurProfile, Post, CollaborationRequest
    from django.shortcuts import get_object_or_404
    from django.db.models import Q
    target_user = get_object_or_404(User, id=user_id, role='entrepreneur')
    profile = get_object_or_404(EntrepreneurProfile, user=target_user)
    posts = Post.objects.filter(author=target_user).order_by('-created_at')
    # Check connection status if viewer is investor
    connection = None
    if request.user.role == 'investor':
        connection = CollaborationRequest.objects.filter(
            investor=request.user, entrepreneur=target_user, status='accepted'
        ).first()
    # For entrepreneurs viewing, show if they are viewing their own profile
    is_self = (request.user == target_user)
    context = {
        'profile_user': target_user,
        'profile': profile,
        'posts': posts,
        'connection': connection,
        'is_self': is_self,
        'viewer_role': request.user.role,
    }
    return render(request, 'profile_detail.html', context)

@login_required
def my_posts(request):
    posts = Post.objects.select_related(
        'author', 'author__entrepreneur_profile', 'author__investor_profile'
    ).prefetch_related('media_files', 'likes', 'comments').filter(author=request.user).order_by('-created_at')
    return render(request, 'my_posts.html', { 'posts': posts })

@login_required
@require_http_methods(["POST"]) 
@transaction.atomic
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    new_content = request.POST.get('content', '').strip()
    post.content = new_content
    post.save(update_fields=['content', 'updated_at'])
    return JsonResponse({ 'success': True })

@login_required
@require_http_methods(["POST"]) 
@transaction.atomic
def remove_post_media(request, post_id, media_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    media = get_object_or_404(PostMedia, id=media_id, post=post)
    media.delete()
    return JsonResponse({ 'success': True })

@login_required
@require_http_methods(["POST"]) 
@transaction.atomic
def reorder_post_media(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    # Expect payload: order=[media_id_1, media_id_2, ...]
    order = request.POST.getlist('order[]') or request.POST.getlist('order')
    try:
        for index, media_id in enumerate(order):
            PostMedia.objects.filter(id=int(media_id), post=post).update(position=index)
        return JsonResponse({ 'success': True })
    except Exception as e:
        return JsonResponse({ 'success': False, 'error': str(e) }, status=400)

@login_required
@require_POST
def toggle_connection(request, target_id):
    # Universal follow/unfollow: any user can follow any user via Favorite
    target = get_object_or_404(User, id=target_id)
    if request.user.id == target.id:
        return JsonResponse({'success': False, 'error': 'Invalid target'})

    fav_qs = Favorite.objects.filter(user=request.user, target_user=target)
    if fav_qs.exists():
        fav_qs.delete()
        return JsonResponse({'success': True, 'connected': False})
    Favorite.objects.create(user=request.user, target_user=target)
    
    # Send notification to target user
    from Investors.services import notify_follow
    notify_follow(request.user, target)
    
    return JsonResponse({'success': True, 'connected': True})

@login_required
@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            receiver = form.cleaned_data['receiver']
            # Privacy enforcement
            if receiver.message_privacy == 'private':
                # Allow if either user follows the other (more permissive friendship)
                is_friend = (request.user.favorites.filter(target_user=receiver).exists() or
                             request.user.favorited_by.filter(user=receiver).exists())
                if not is_friend:
                    return HttpResponseForbidden('User only accepts messages from friends.')
            msg = form.save(commit=False)
            msg.sender = request.user
            # Handle file upload
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                msg.file_name = uploaded_file.name
                msg.file_type = uploaded_file.content_type
                msg.file_data = uploaded_file.read()
                msg.file_size = uploaded_file.size
            msg.save()
            serializer = MessageSerializer(msg)
            # TODO: Trigger WebSocket event for real-time update
            return JsonResponse({'success': True, 'message': serializer.data})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def messages_page(request):
    """Main messages page for entrepreneurs"""
    # Recent chats = users you've exchanged messages with OR you follow
    recent_users = set()
    # Users you've messaged (sent or received)
    from .models import Message, Favorite
    
    msg_users = set()
    # Get all messages where user is sender or receiver
    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).distinct()
    
    # Extract unique user IDs from sender and receiver fields
    for msg in messages:
        if msg.sender != request.user:
            msg_users.add(msg.sender.id)
        if msg.receiver != request.user:
            msg_users.add(msg.receiver.id)
    
    # Add users to recent_users set, respecting privacy settings
    for uid in msg_users:
        try:
            u = User.objects.get(id=uid)
            # For private users, only show if there's a connection
            if u.message_privacy == 'public':
                recent_users.add(u)
            else:
                # Check if there's any connection (following or followed)
                is_connected = (request.user.favorites.filter(target_user=u).exists() or
                               request.user.favorited_by.filter(user=u).exists())
                if is_connected:
                    recent_users.add(u)
        except User.DoesNotExist:
            pass
    
    # Add users you follow (favorites)
    for f in Favorite.objects.filter(user=request.user).select_related('target_user'):
        recent_users.add(f.target_user)
    
    # Add users who follow you
    for f in Favorite.objects.filter(target_user=request.user).select_related('user'):
        recent_users.add(f.user)
    
    # Limit and sort
    recent_list = sorted(recent_users, key=lambda u: (u.get_full_name() or u.email))[:25]
    
    return render(request, 'messages/index.html', { 'recents': recent_list })


@login_required
def message_search(request):
    """Search public users or friends if private; enforce privacy server-side."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({ 'results': [] })
    
    # Who is allowed to appear?
    # public users OR private users who have any connection with current user
    allowed_ids = set(User.objects.filter(message_privacy='public').values_list('id', flat=True))
    
    # Private users who follow current user OR are followed by current user
    private_friend_ids = set()
    # Users I follow
    following_ids = set(Favorite.objects.filter(user=request.user).values_list('target_user_id', flat=True))
    # Users who follow me
    follower_ids = set(Favorite.objects.filter(target_user=request.user).values_list('user_id', flat=True))
    
    # Add private users who have any connection
    private_users = User.objects.filter(message_privacy='private')
    for private_user in private_users:
        if (private_user.id in following_ids or private_user.id in follower_ids):
            private_friend_ids.add(private_user.id)
    
    allowed_ids.update(private_friend_ids)
    allowed_ids.discard(request.user.id)

    qs = User.objects.filter(id__in=list(allowed_ids)).filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
    ).select_related('entrepreneur_profile', 'investor_profile')[:20]

    def img64(u):
        try:
            if hasattr(u, 'entrepreneur_profile') and u.entrepreneur_profile.image:
                import base64
                return 'data:image/jpeg;base64,' + base64.b64encode(u.entrepreneur_profile.image).decode('utf-8')
            if hasattr(u, 'investor_profile') and u.investor_profile.image:
                import base64
                return 'data:image/jpeg;base64,' + base64.b64encode(u.investor_profile.image).decode('utf-8')
        except Exception:
            return ''
        return ''

    def profile_url(u):
        if u.role == 'investor':
            return f"/investor/profile/{u.id}/"
        else:
            return f"/entrepreneur/profile/{u.id}/"

    results = [{
        'id': u.id,
        'name': u.get_full_name() or u.email,
        'role': u.role,
        'avatar': img64(u),
        'profile_url': profile_url(u),
        'is_private': u.message_privacy == 'private'
    } for u in qs]
    
    return JsonResponse({ 'results': results })


@login_required
def get_messages(request, user_id):
    # Enforce privacy: only show messages if allowed
    other = User.objects.get(id=user_id)
    if other.message_privacy == 'private':
        is_friend = (request.user.favorites.filter(target_user=other).exists() or
                     request.user.favorited_by.filter(user=other).exists())
        if not is_friend:
            return HttpResponseForbidden('User only allows messages from friends.')
    qs = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other)) |
        (Q(sender=other) & Q(receiver=request.user))
    ).order_by('timestamp')
    # Mark unread messages as read
    qs.filter(receiver=request.user, is_read=False).update(is_read=True)
    serializer = MessageSerializer(qs, many=True)
    return JsonResponse({'messages': serializer.data})


@login_required
def create_startup(request):
    """Create a new startup for the entrepreneur"""
    if request.user.role != 'entrepreneur':
        messages.error(request, 'Access denied. You are not an entrepreneur.')
        return redirect('home')
    
    if request.method == 'POST':
        form = StartupForm(request.POST, request.FILES)
        if form.is_valid():
            startup = form.save(commit=False)
            startup.entrepreneur = request.user
            
            # Handle logo upload
            if 'logo' in request.FILES:
                logo_file = request.FILES['logo']
                startup.logo = logo_file.read()
            
            startup.save()
            
            # Send notification to all investors
            from Investors.services import notify_startup_created
            notify_startup_created(startup)
            
            messages.success(request, f'Startup "{startup.name}" created successfully!')
            return redirect('investors:create_funding_round')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StartupForm()
    
    return render(request, 'Entrepreneurs/create_startup.html', {'form': form})

