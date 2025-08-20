
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from Entrepreneurs.models import User
from .models import InvestorProfile, InvestorPortfolio, InvestmentDocument
from .forms import InvestorRegistrationForm, InvestorProfileForm, MessageSettingsForm
from django.http import JsonResponse
from Entrepreneurs.models import Post, PostMedia
from Entrepreneurs.forms import PostForm
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponseForbidden
from Entrepreneurs.models import Post, Comment, CollaborationRequest, EntrepreneurProfile, Favorite, Message
from Entrepreneurs.forms import CommentForm
from django.shortcuts import get_object_or_404
import base64
from django.db import transaction
from django.db.models import Q

@login_required
def message_settings(request):
    if request.method == 'POST':
        form = MessageSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('investors:messages')
    else:
        form = MessageSettingsForm(instance=request.user)
    return render(request, 'messages/settings.html', { 'form': form })

@login_required
def messages_page(request):
    # Recent chats = users you've exchanged messages with OR you follow
    recent_users = set()
    # Users you've messaged (sent or received)
    from Entrepreneurs.models import Message
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
    """Get messages between current user and another user"""
    from Entrepreneurs.models import User
    
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
    
    # Serialize messages
    messages_data = []
    for msg in qs:
        message_data = {
            'id': msg.id,
            'content': msg.content,
            'sender': msg.sender.id,
            'receiver': msg.receiver.id,
            'timestamp': msg.timestamp.isoformat(),
            'is_read': msg.is_read,
            'message_type': msg.message_type,
            'file_name': msg.file_name,
            'file_type': msg.file_type,
            'file_size': msg.file_size,
            'file_base64': msg.file_data.decode('utf-8') if msg.file_data else None
        }
        messages_data.append(message_data)
    
    return JsonResponse({'messages': messages_data})


def investor_register(request):
    if request.method == 'POST':
        form = InvestorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'investor'
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create a basic profile with default values
            profile = InvestorProfile.objects.create(user=user)
            
            messages.success(request, 'Registration successful! Please log in to continue.')
            return redirect('investors:login')  # Redirect to login page instead of auto-login
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = InvestorRegistrationForm()
    
    return render(request, 'Investors/investor_registration.html', {'form': form})


def index(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'cofound_landing.html')


def investor_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'Investors/investor_login.html')
        
        user = authenticate(request, email=email, password=password)
        if user is not None and user.role == 'investor':
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('home')  # Redirect to base.html (common home)
        else:
            messages.error(request, 'Invalid credentials or not an investor.')
    
    return render(request, 'Investors/investor_login.html')


def investor_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')  # Redirect to landing page


@login_required
def home(request):
    """Common home view for both investors and entrepreneurs"""
    if not request.user.is_authenticated:
        return redirect('index')

    # Get the appropriate profile based on user role
    if request.user.role == 'investor':
        profile = InvestorProfile.objects.get_or_create(user=request.user)[0]
    else:
        profile = EntrepreneurProfile.objects.get_or_create(user=request.user)[0]

    # Current accepted CollaborationRequest connections
    accepted = CollaborationRequest.objects.filter(
        Q(investor=request.user, status='accepted') | Q(entrepreneur=request.user, status='accepted')
    )
    connected_user_ids = set()
    for r in accepted:
        connected_user_ids.add(r.investor_id)
        connected_user_ids.add(r.entrepreneur_id)
    connected_user_ids.discard(request.user.id)

    # Current favorites (same-role follows)
    favorites = Favorite.objects.filter(user=request.user).select_related('target_user')
    for f in favorites:
        connected_user_ids.add(f.target_user_id)

    # Suggestions: both roles, exclude already connected and self
    users_qs = User.objects.exclude(id=request.user.id).select_related(
        'entrepreneur_profile', 'investor_profile'
    )
    suggestions_qs = users_qs.exclude(id__in=connected_user_ids)
    suggestions = list(suggestions_qs[:5])

    # Build mutual friends from both accepted graph and favorites graph
    def neighbors(u: User):
        nbrs = set()
        # collab neighbors
        for r in CollaborationRequest.objects.filter(
            Q(investor=u, status='accepted') | Q(entrepreneur=u, status='accepted')
        ):
            nbrs.add(r.investor)
            nbrs.add(r.entrepreneur)
        # favorites neighbors (following)
        for f in Favorite.objects.filter(user=u).select_related('target_user'):
            nbrs.add(f.target_user)
        if u in nbrs:
            nbrs.discard(u)
        return nbrs

    my_neighbors = neighbors(request.user)
    second_degree = set()
    for n in my_neighbors:
        second_degree.update(neighbors(n))
    # Exclude already connected/self and direct neighbors
    rs_mutual = [u for u in second_degree if u.id not in connected_user_ids and u.id != request.user.id and u not in my_neighbors]

    # Same industry suggestions (role-aware terms) still exclude connected
    def split_terms(s):
        if not s:
            return set()
        return set(t.strip().lower() for t in s.split(',') if t.strip())

    rs_industry = []
    if request.user.role == 'investor':
        inv_terms = split_terms(profile.preferred_industries)
        for ep in EntrepreneurProfile.objects.select_related('user').all():
            if ep.user.id in connected_user_ids or ep.user.id == request.user.id:
                continue
            if inv_terms and (split_terms(ep.industries) & inv_terms):
                rs_industry.append(ep.user)
    else:
        ep_terms = split_terms(profile.industries)
        for ip in InvestorProfile.objects.select_related('user').all():
            if ip.user.id in connected_user_ids or ip.user.id == request.user.id:
                continue
            if ep_terms and (split_terms(ip.preferred_industries) & ep_terms):
                rs_industry.append(ip.user)

    # Posts feed unchanged...
    try:
        posts = Post.objects.select_related(
            'author', 
            'author__entrepreneur_profile', 
            'author__investor_profile'
        ).prefetch_related(
            'media_files', 'likes', 'comments',
            'comments__author', 'comments__author__entrepreneur_profile', 'comments__author__investor_profile'
        ).order_by('-created_at')
    except Exception as e:
        print(f"Error fetching posts: {e}")
        posts = []

    context = {
        'profile': profile,
        'users': users_qs,
        'posts': posts,
        'suggestions': suggestions,
        'rs_mutual': rs_mutual[:5],
        'rs_industry': rs_industry[:5],
    }
    return render(request, 'home.html', context)


@login_required
def investor_dashboard(request):
    if request.user.role != 'investor':
        messages.error(request, 'Access denied. You are not an investor.')
        return redirect('investors:login')
        
    profile = InvestorProfile.objects.get_or_create(user=request.user)[0]
    context = {
        'profile': profile,
    }
    return render(request, 'Investors/dashboard.html', context)


@login_required
def investor_profile(request):
    if request.user.role != 'investor':
        messages.error(request, 'Access denied. You are not an investor.')
        return redirect('investors:login')
    profile = InvestorProfile.objects.get_or_create(user=request.user)[0]
    if request.method == 'POST':
        form = InvestorProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)
            image_file = request.FILES.get('image_upload')
            if image_file:
                profile.image = image_file.read()
            profile.save()
            form.save_m2m()
            messages.success(request, 'Profile updated successfully!')
            return redirect('investors:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = InvestorProfileForm(instance=profile, user=request.user)
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'Investors/profile.html', context)


@login_required
def upload_investment_document(request):
    """Handle investment document uploads"""
    if request.user.role != 'investor':
        messages.error(request, 'Access denied. You are not an investor.')
        return redirect('investors:login')
    
    if request.method == 'POST':
        form = InvestmentDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.investor = request.user
            
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
            
            return redirect('investors:profile')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    return redirect('investors:profile')


@login_required
def create_post(request):
    """Create post view for investors - uses same logic as entrepreneurs"""
    if request.method == 'POST':
        # Check if we have any content or media before form validation
        content = request.POST.get('content', '').strip()
        images = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')
        documents = request.FILES.getlist('documents')
        
        # Validate that we have at least one type of content
        if not content and not images and not videos and not documents:
            return JsonResponse({
                'success': False, 
                'errors': {'general': ['Please provide some content or media for your post.']}
            })
        
        # Create form with data
        form = PostForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                
                # Only save each file once
                for image in images:
                    PostMedia.objects.create(
                        post=post,
                        media_type='image',
                        file_name=image.name,
                        file_type=image.content_type,
                        file_data=image.read(),
                        file_size=image.size
                    )
                
                # Only save each file once
                for video in videos:
                    PostMedia.objects.create(
                        post=post,
                        media_type='video',
                        file_name=video.name,
                        file_type=video.content_type,
                        file_data=video.read(),
                        file_size=video.size
                    )
                
                # Only save each file once
                for document in documents:
                    PostMedia.objects.create(
                        post=post,
                        media_type='document',
                        file_name=document.name,
                        file_type=document.content_type,
                        file_data=document.read(),
                        file_size=document.size
                    )
                
                messages.success(request, 'Post created successfully!')
                return JsonResponse({'success': True, 'post_id': post.id})
            except Exception as e:
                return JsonResponse({'success': False, 'errors': {'general': [f'Error creating post: {str(e)}']}})
        else:
            # Convert form errors to a more readable format
            error_dict = {}
            for field, errors in form.errors.items():
                error_dict[field] = [str(error) for error in errors]
            return JsonResponse({'success': False, 'errors': error_dict})
    
    return JsonResponse({'success': False, 'errors': {'general': ['Invalid request method']}})

@login_required
def like_post(request, post_id):
    """Like post view for investors - uses same logic as entrepreneurs"""
    try:
        post = Post.objects.get(id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        
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

        # Safely resolve and encode profile image
        image_bytes = None
        try:
            if hasattr(comment.author, 'investor_profile') and comment.author.investor_profile.image:
                image_bytes = comment.author.investor_profile.image
            elif hasattr(comment.author, 'entrepreneur_profile') and comment.author.entrepreneur_profile.image:
                image_bytes = comment.author.entrepreneur_profile.image
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
@require_POST
def toggle_save(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if post.saved_by.filter(id=user.id).exists():
        post.saved_by.remove(user)
        return JsonResponse({'success': True, 'saved': False})
    else:
        post.saved_by.add(user)
        return JsonResponse({'success': True, 'saved': True})

@login_required
def saved_posts(request):
    posts = Post.objects.select_related(
        'author', 'author__entrepreneur_profile', 'author__investor_profile'
    ).prefetch_related('media_files', 'likes', 'comments').filter(saved_by=request.user).order_by('-created_at')
    context = {
        'posts': posts,
        'saved_page': True,
    }
    return render(request, 'saved_posts.html', context)

@login_required
def find_startups(request):
    if request.user.role != 'investor':
        messages.error(request, 'Access denied.')
        return redirect('home')
    startups = EntrepreneurProfile.objects.select_related('user').all()
    return render(request, 'find_startups.html', { 'startups': startups })

@login_required
@require_POST
def investor_connect(request, target_id):
    if request.user.role != 'investor':
        return JsonResponse({'success': False, 'error': 'Access denied'})
    try:
        target = User.objects.get(id=target_id, role='entrepreneur')
        CollaborationRequest.objects.create(investor=request.user, entrepreneur=target, status='pending')
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def investor_profile_detail(request, user_id):
    from Entrepreneurs.models import EntrepreneurProfile, Post, CollaborationRequest
    from .models import InvestorProfile
    from django.shortcuts import get_object_or_404
    from django.db.models import Q
    target_user = get_object_or_404(User, id=user_id, role='investor')
    profile = get_object_or_404(InvestorProfile, user=target_user)
    posts = Post.objects.filter(author=target_user).order_by('-created_at')
    # Check connection status if viewer is entrepreneur
    connection = None
    if request.user.role == 'entrepreneur':
        connection = CollaborationRequest.objects.filter(
            investor=target_user, entrepreneur=request.user, status='accepted'
        ).first()
    # For investors viewing, show if they are viewing their own profile
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
    # Universal follow/unfollow via Favorite regardless of roles
    target = get_object_or_404(User, id=target_id)
    if request.user.id == target.id:
        return JsonResponse({'success': False, 'error': 'Invalid target'})
    fav = Favorite.objects.filter(user=request.user, target_user=target)
    if fav.exists():
        fav.delete()
        return JsonResponse({'success': True, 'connected': False})
    Favorite.objects.create(user=request.user, target_user=target)
    return JsonResponse({'success': True, 'connected': True})

@login_required
def my_network(request):
    # Build connections as union of accepted collab and favorites
    conns_qs = CollaborationRequest.objects.filter(
        Q(investor=request.user, status='accepted') | Q(entrepreneur=request.user, status='accepted')
    ).select_related('investor', 'entrepreneur', 'investor__investor_profile', 'entrepreneur__entrepreneur_profile')
    connections = []
    connected_user_ids = set()
    for r in conns_qs:
        other = r.investor if r.investor_id != request.user.id else r.entrepreneur
        if other.id != request.user.id:
            connections.append(other)
            connected_user_ids.add(other.id)
    for f in Favorite.objects.filter(user=request.user).select_related('target_user'):
        if f.target_user_id != request.user.id and f.target_user_id not in connected_user_ids:
            connections.append(f.target_user)
            connected_user_ids.add(f.target_user_id)

    # mutual via neighbors-of-neighbors using union graph
    def neighbors(u: User):
        nbrs = set()
        for r in CollaborationRequest.objects.filter(
            Q(investor=u, status='accepted') | Q(entrepreneur=u, status='accepted')
        ):
            nbrs.add(r.investor)
            nbrs.add(r.entrepreneur)
        for f in Favorite.objects.filter(user=u).select_related('target_user'):
            nbrs.add(f.target_user)
        if u in nbrs:
            nbrs.discard(u)
        return nbrs

    my_neighbors = neighbors(request.user)
    second_degree = set()
    for n in my_neighbors:
        second_degree.update(neighbors(n))
    mutual_suggestions = [u for u in second_degree if u.id not in connected_user_ids and u.id != request.user.id and u not in my_neighbors]

    # same-industry re-used from home logic
    def split_terms(s):
        if not s:
            return set()
        return set(t.strip().lower() for t in s.split(',') if t.strip())

    industry_suggestions = []
    if request.user.role == 'investor':
        inv = InvestorProfile.objects.get_or_create(user=request.user)[0]
        inv_terms = split_terms(inv.preferred_industries)
        for ep in EntrepreneurProfile.objects.select_related('user').all():
            if ep.user.id in connected_user_ids or ep.user.id == request.user.id:
                continue
            if inv_terms and (split_terms(ep.industries) & inv_terms):
                industry_suggestions.append(ep.user)
    else:
        ep = EntrepreneurProfile.objects.get_or_create(user=request.user)[0]
        ep_terms = split_terms(ep.industries)
        for ip in InvestorProfile.objects.select_related('user').all():
            if ip.user.id in connected_user_ids or ip.user.id == request.user.id:
                continue
            if ep_terms and (split_terms(ip.preferred_industries) & ep_terms):
                industry_suggestions.append(ip.user)

    context = {
        'connections': connections,
        'mutual_suggestions': mutual_suggestions,
        'industry_suggestions': industry_suggestions,
    }
    return render(request, 'my_network.html', context)

@login_required
def network_data(request):
    # Union of favorites and accepted collab for connections
    conns_qs = CollaborationRequest.objects.filter(
        Q(investor=request.user, status='accepted') | Q(entrepreneur=request.user, status='accepted')
    ).select_related('investor', 'entrepreneur', 'investor__investor_profile', 'entrepreneur__entrepreneur_profile')
    connections = []
    connected_ids = set()
    for r in conns_qs:
        other = r.investor if r.investor_id != request.user.id else r.entrepreneur
        if other.id != request.user.id:
            connections.append(other)
            connected_ids.add(other.id)
    for f in Favorite.objects.filter(user=request.user).select_related('target_user'):
        if f.target_user_id != request.user.id and f.target_user_id not in connected_ids:
            connections.append(f.target_user)
            connected_ids.add(f.target_user_id)

    def img64(u):
        try:
            if hasattr(u, 'entrepreneur_profile') and u.entrepreneur_profile.image:
                import base64
                return base64.b64encode(u.entrepreneur_profile.image).decode('utf-8')
            if hasattr(u, 'investor_profile') and u.investor_profile.image:
                import base64
                return base64.b64encode(u.investor_profile.image).decode('utf-8')
        except Exception:
            return ''
        return ''

    def neighbors(u: User):
        nbrs = set()
        for r in CollaborationRequest.objects.filter(
            Q(investor=u, status='accepted') | Q(entrepreneur=u, status='accepted')
        ):
            nbrs.add(r.investor)
            nbrs.add(r.entrepreneur)
        for f in Favorite.objects.filter(user=u).select_related('target_user'):
            nbrs.add(f.target_user)
        if u in nbrs:
            nbrs.discard(u)
        return nbrs

    my_neighbors = neighbors(request.user)
    second_degree = set()
    for n in my_neighbors:
        second_degree.update(neighbors(n))
    mutual = [u for u in second_degree if u.id not in connected_ids and u.id != request.user.id and u not in my_neighbors]

    def split_terms(s):
        if not s:
            return set()
        return set(t.strip().lower() for t in s.split(',') if t.strip())

    industry = []
    if request.user.role == 'investor':
        inv = InvestorProfile.objects.get_or_create(user=request.user)[0]
        inv_terms = split_terms(inv.preferred_industries)
        for ep in EntrepreneurProfile.objects.select_related('user').all():
            if ep.user.id in connected_ids or ep.user.id == request.user.id:
                continue
            if inv_terms and (split_terms(ep.industries) & inv_terms):
                industry.append(ep.user)
    else:
        ep = EntrepreneurProfile.objects.get_or_create(user=request.user)[0]
        ep_terms = split_terms(ep.industries)
        for ip in InvestorProfile.objects.select_related('user').all():
            if ip.user.id in connected_ids or ip.user.id == request.user.id:
                continue
            if ep_terms and (split_terms(ip.preferred_industries) & ep_terms):
                industry.append(ip.user)

    def to_json(u):
        return {
            'id': u.id,
            'name': u.get_full_name() or u.email,
            'role': u.role,
            'avatar': img64(u),
            'org': (getattr(getattr(u, 'entrepreneur_profile', None), 'company_name', '') if u.role == 'entrepreneur' else getattr(getattr(u, 'investor_profile', None), 'firm_name', ''))
        }

    return JsonResponse({
        'connections': [to_json(u) for u in connections],
        'mutual': [to_json(u) for u in mutual],
        'industry': [to_json(u) for u in industry],
    })


