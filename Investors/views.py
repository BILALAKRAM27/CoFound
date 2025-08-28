
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from Entrepreneurs.models import User, Favorite, CollaborationRequest, Notification, ActivityLog
from .models import InvestorProfile, InvestorPortfolio, InvestmentDocument, FundingRound, InvestmentCommitment
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
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import FundingRound, InvestmentCommitment
from django.db.models import Sum
from decimal import Decimal
from .services import NotificationService
from django.db import models
from .forms import MeetingRequestForm
from Entrepreneurs.models import Meeting
from allauth.account.signals import user_signed_up
from django.dispatch import receiver

# Utility to add percent_raised to rounds
def annotate_percent_raised(rounds):
    for r in rounds:
        try:
            total = r.total_committed()
            r.percent_raised = float(total) / float(r.target_goal) * 100 if r.target_goal else 0
        except Exception:
            r.percent_raised = 0
    return rounds

@login_required
def message_settings(request):
    if request.method == 'POST':
        form = MessageSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # Redirect to the next parameter or default to messages page
            next_url = request.POST.get('next') or request.GET.get('next') or 'investors:messages'
            return redirect(next_url)
    else:
        form = MessageSettingsForm(instance=request.user)
    return render(request, 'messages/settings.html', { 'form': form })

@login_required
def messages_page(request):
    # Recent chats = users you've exchanged messages with OR you follow
    recent_users = set()
    from Entrepreneurs.models import Message, Favorite
    msg_users = set()
    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).distinct()
    for msg in messages:
        if msg.sender != request.user:
            msg_users.add(msg.sender.id)
        if msg.receiver != request.user:
            msg_users.add(msg.receiver.id)
    for uid in msg_users:
        try:
            u = User.objects.get(id=uid)
            is_connected = (request.user.favorites.filter(target_user=u).exists() or
                            request.user.favorited_by.filter(user=u).exists())
            if u.message_privacy == 'public' or is_connected:
                recent_users.add(u)
        except User.DoesNotExist:
            pass
    for f in Favorite.objects.filter(user=request.user).select_related('target_user'):
        u = f.target_user
        is_connected = (request.user.favorites.filter(target_user=u).exists() or
                        request.user.favorited_by.filter(user=u).exists())
        if u.message_privacy == 'public' or is_connected:
            recent_users.add(u)
    for f in Favorite.objects.filter(target_user=request.user).select_related('user'):
        u = f.user
        is_connected = (request.user.favorites.filter(target_user=u).exists() or
                        request.user.favorited_by.filter(user=u).exists())
        if u.message_privacy == 'public' or is_connected:
            recent_users.add(u)
    recent_users_with_data = []
    total_unread_count = 0
    for u in recent_users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=u)) |
            (Q(sender=u) & Q(receiver=request.user))
        ).order_by('-timestamp').first()
        unread_count = Message.objects.filter(sender=u, receiver=request.user, is_read=False).count()
        total_unread_count += unread_count
        if last_message:
            recent_users_with_data.append({
                'user': u,
                'last_message': last_message,
                'unread_count': unread_count,
                'last_message_time': last_message.timestamp
            })
    recent_users_with_data.sort(key=lambda x: x['last_message_time'], reverse=True)
    recent_list = [item['user'] for item in recent_users_with_data[:25]]
    unread_counts = {item['user'].id: item['unread_count'] for item in recent_users_with_data[:25]}
    last_messages = {item['user'].id: item['last_message'] for item in recent_users_with_data[:25]}
    last_message_times = {item['user'].id: item['last_message_time'] for item in recent_users_with_data[:25]}
    return render(request, 'messages/index.html', {
        'recents': recent_list,
        'unread_counts': unread_counts,
        'last_messages': last_messages,
        'last_message_times': last_message_times,
        'total_unread_count': total_unread_count
    })

@login_required
def message_search(request):
    """Search public users or friends if private; enforce privacy server-side."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({ 'results': [] })
    # All users except self
    qs = User.objects.exclude(id=request.user.id)
    if q:
        qs = qs.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))
    qs = qs.select_related('entrepreneur_profile', 'investor_profile')[:20]

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

    results = []
    for u in qs:
        is_connected = (request.user.favorites.filter(target_user=u).exists() or
                        request.user.favorited_by.filter(user=u).exists())
        can_message = (u.message_privacy == 'public') or is_connected
        results.append({
            'id': u.id,
            'name': u.get_full_name() or u.email,
            'role': u.role,
            'avatar': img64(u),
            'profile_url': profile_url(u),
            'is_private': u.message_privacy == 'private',
            'can_message': can_message,
        })
    return JsonResponse({ 'results': results })


@login_required
def get_messages(request, user_id):
    """Get messages between current user and another user"""
    from Entrepreneurs.models import User
    
    # Check if this is a direct access (not an AJAX request)
    # If it's a direct browser access, redirect to the chat page
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # This is a direct browser access, redirect to the chat page
        current_user_role = request.user.role
        messages_url = '/investor/messages/' if current_user_role == 'investor' else '/entrepreneur/messages/'
        redirect_url = f"{messages_url}?open_chat={user_id}"
        return redirect(redirect_url)
    
    # This is an AJAX request, return JSON data
    try:
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
                'file_base64': base64.b64encode(msg.file_data).decode('utf-8') if msg.file_data else None
            }
            messages_data.append(message_data)
        
        return JsonResponse({'messages': messages_data})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


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
    
    from Entrepreneurs.models import Favorite, CollaborationRequest, Notification
    from .models import InvestmentCommitment, FundingRound
    from .services import NotificationService
    
    profile = InvestorProfile.objects.get_or_create(user=request.user)[0]
    
    # Calculate connections (both favorites and accepted collaboration requests)
    favorites_count = Favorite.objects.filter(user=request.user).count()
    accepted_requests = CollaborationRequest.objects.filter(
        Q(investor=request.user, status='accepted') | 
        Q(entrepreneur=request.user, status='accepted')
    ).count()
    total_connections = favorites_count + accepted_requests
    
    # Calculate profile views (from activity logs)
    profile_views = ActivityLog.objects.filter(
        action='view_profile',
        details__contains=f'viewed {request.user.get_full_name() or request.user.email}'
    ).count()
    
    # Calculate investment deals
    investment_deals = InvestmentCommitment.objects.filter(investor=request.user).count()
    
    # Calculate total invested
    total_invested = InvestmentCommitment.objects.filter(investor=request.user).aggregate(
        total=models.Sum('amount')
    )['total'] or 0
    
    # Get recent notifications (top 3)
    recent_notifications = NotificationService.get_user_notifications(request.user, limit=3)
    
    # Get recent investment commitments
    recent_investments = InvestmentCommitment.objects.filter(
        investor=request.user
    ).select_related('funding_round', 'funding_round__startup').order_by('-committed_at')[:5]
    
    # Get portfolio companies (startups they've invested in)
    portfolio_companies = FundingRound.objects.filter(
        investments__investor=request.user
    ).values_list('startup__name', flat=True).distinct()
    
    sidebar_connections_count = total_connections
    sidebar_posts_count = request.user.posts.count() if hasattr(request.user, 'posts') else 0
    sidebar_profile_views = profile.profile_views
    context = {
        'profile': profile,
        'total_connections': total_connections,
        'profile_views': profile.profile_views,
        'investment_deals': investment_deals,
        'total_invested': total_invested,
        'recent_notifications': recent_notifications,
        'recent_investments': recent_investments,
        'portfolio_companies': portfolio_companies,
        'sidebar_connections_count': sidebar_connections_count,
        'sidebar_posts_count': sidebar_posts_count,
        'sidebar_profile_views': sidebar_profile_views,
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
                
                # Send notification to followers
                from .services import notify_post_created
                notify_post_created(post)
                
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
            # Send notification to post author
            from .services import notify_like
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

        # Send notification to post author
        from .services import notify_comment
        notify_comment(post, request.user)

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
    # Increment profile views if not self
    if not is_self:
        profile.profile_views = (profile.profile_views or 0) + 1
        profile.save(update_fields=["profile_views"])
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
    
    # Send notification to target user
    from .services import notify_follow
    notify_follow(request.user, target)
    
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

@login_required
def create_funding_round(request):
    if request.user.role != 'entrepreneur':
        return redirect('home')
    
    # Get user's startups
    from Entrepreneurs.models import Startup
    user_startups = Startup.objects.filter(entrepreneur=request.user).order_by('name')
    
    errors = {}
    initial = {}
    
    if request.method == 'POST':
        round_name = request.POST.get('round_name', '').strip()
        target_goal = request.POST.get('target_goal', '').strip()
        equity_offered = request.POST.get('equity_offered', '').strip()
        deadline = request.POST.get('deadline', '').strip()
        startup_id = request.POST.get('startup_id', '').strip()
        
        initial = {
            'round_name': round_name,
            'target_goal': target_goal,
            'equity_offered': equity_offered,
            'deadline': deadline,
            'startup_id': startup_id,
        }
        
        # Validation
        if not round_name:
            errors['round_name'] = 'Round name is required.'
        if not target_goal or float(target_goal) <= 0:
            errors['target_goal'] = 'Target goal must be a positive number.'
        if not equity_offered or float(equity_offered) <= 0 or float(equity_offered) > 100:
            errors['equity_offered'] = 'Equity offered must be between 0 and 100%.'
        if not deadline:
            errors['deadline'] = 'Deadline is required.'
        else:
            try:
                # Handle datetime-local input format (YYYY-MM-DDTHH:MM)
                if 'T' in deadline:
                    # Parse the datetime-local format manually
                    from datetime import datetime
                    # Remove any timezone info and parse as local time
                    deadline_clean = deadline.split('+')[0].split('Z')[0]
                    
                    # Handle different formats: YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS
                    if deadline_clean.count(':') == 1:
                        deadline_dt = datetime.strptime(deadline_clean, '%Y-%m-%dT%H:%M')
                    else:
                        deadline_dt = datetime.strptime(deadline_clean, '%Y-%m-%dT%H:%M:%S')
                    
                    # Make it timezone-aware
                    deadline_dt = timezone.make_aware(deadline_dt)
                else:
                    # Fallback for other formats
                    from datetime import datetime
                    deadline_dt = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')
                    deadline_dt = timezone.make_aware(deadline_dt)
                
                if deadline_dt <= timezone.now():
                    errors['deadline'] = 'Deadline must be in the future.'
            except Exception as e:
                errors['deadline'] = f'Invalid deadline format. Please use the date picker.'
        
        # Startup validation
        if not startup_id:
            errors['startup_id'] = 'Please select a startup.'
        else:
            try:
                startup = Startup.objects.get(id=startup_id, entrepreneur=request.user)
            except Startup.DoesNotExist:
                errors['startup_id'] = 'Invalid startup selected.'
                startup = None
        
        if not errors and startup:
            fr = FundingRound.objects.create(
                startup=startup,
                round_name=round_name,
                target_goal=target_goal,
                equity_offered=equity_offered,
                deadline=deadline_dt
            )
            
            # Send notification to all investors
            from .services import notify_funding_round_created
            notify_funding_round_created(fr)
            
            return redirect('investors:funding_round_detail', round_id=fr.id)
    
    return render(request, 'Investors/create_funding_round.html', {
        'errors': errors, 
        'initial': initial, 
        'user': request.user,
        'user_startups': user_startups
    })

@login_required
@require_POST
def commit_investment(request):
    try:
        if request.user.role != 'investor':
            return JsonResponse({'success': False, 'error': 'Only investors can commit investments.'}, status=403)
        
        round_id = request.POST.get('funding_round_id')
        amount = request.POST.get('amount')
        
        if not all([round_id, amount]):
            return JsonResponse({'success': False, 'error': 'Missing required fields.'}, status=400)
        
        # Validate amount
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                return JsonResponse({'success': False, 'error': 'Amount must be greater than 0.'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid amount format.'}, status=400)
        
        # Get funding round
        try:
            fr = FundingRound.objects.get(id=round_id, status='active')
        except FundingRound.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Funding round not found or not active.'}, status=404)
        
        # Check deadline
        if fr.deadline < timezone.now():
            return JsonResponse({'success': False, 'error': 'Funding round deadline has passed.'}, status=400)
        
        # Create or get commitment
        try:
            ic, created = InvestmentCommitment.objects.get_or_create(
                funding_round=fr, investor=request.user,
                defaults={'amount': amount_decimal}
            )
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Error creating commitment: {str(e)}'
            }, status=500)
        
        if not created:
            return JsonResponse({'success': False, 'error': 'You have already committed to this round.'}, status=400)
        
        # Calculate equity share safely
        try:
            equity_share = ic.equity_share
        except Exception as e:
            # If equity calculation fails, calculate manually
            try:
                equity_share = (amount_decimal / fr.target_goal) * fr.equity_offered
            except Exception as calc_error:
                return JsonResponse({
                    'success': False, 
                    'error': f'Error calculating equity share: {str(calc_error)}'
                }, status=500)
        
        # Convert amount to float safely
        try:
            amount_float = float(amount_decimal)
        except (ValueError, TypeError):
            amount_float = float(str(amount_decimal))
        
        # Send notification to startup owner
        from .services import notify_investment_committed
        notify_investment_committed(fr, request.user, amount_decimal)
        
        return JsonResponse({
            'success': True, 
            'commitment_id': ic.id, 
            'equity_share': equity_share,
            'amount': amount_float
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Unexpected error: {str(e)}'
        }, status=500)

@login_required
@require_POST
def close_funding_round(request):
    if request.user.role != 'entrepreneur':
        return JsonResponse({'success': False, 'error': 'Only startups can close funding rounds.'}, status=403)
    round_id = request.POST.get('funding_round_id')
    if not round_id:
        return JsonResponse({'success': False, 'error': 'Missing funding_round_id.'}, status=400)
    try:
        fr = FundingRound.objects.get(id=round_id, startup__entrepreneur=request.user)
        if fr.status != 'active':
            return JsonResponse({'success': False, 'error': 'Round is already closed.'}, status=400)
        if fr.total_committed() >= fr.target_goal:
            fr.status = 'successful'
        else:
            fr.status = 'failed'
        fr.save(update_fields=['status', 'updated_at'])
        return JsonResponse({'success': True, 'status': fr.status})
    except FundingRound.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Funding round not found or not owned by user.'}, status=404)

@login_required
def funding_rounds_list(request):
    if request.user.role == 'entrepreneur':
        rounds = FundingRound.objects.filter(startup__entrepreneur=request.user).order_by('-created_at')
    else:
        rounds = FundingRound.objects.all().order_by('-created_at')
    rounds = annotate_percent_raised(rounds)
    return render(request, 'Investors/funding_rounds.html', {'rounds': rounds, 'user': request.user})

@login_required
def funding_round_detail(request, round_id):
    round = FundingRound.objects.select_related('startup').get(id=round_id)
    commitments = InvestmentCommitment.objects.filter(funding_round=round).select_related('investor')
    
    # Add safe equity_share calculation for each commitment
    for commitment in commitments:
        try:
            commitment.safe_equity_share = commitment.equity_share
        except (ValueError, TypeError, AttributeError):
            commitment.safe_equity_share = 0
    
    round.percent_raised = float(round.total_committed()) / float(round.target_goal) * 100 if round.target_goal else 0
    return render(request, 'Investors/funding_round_detail.html', {
        'round': round,
        'commitments': commitments,
        'user': request.user
    })

@login_required
def startup_dashboard_offers(request):
    if request.user.role != 'entrepreneur':
        return redirect('home')
    rounds = FundingRound.objects.filter(startup__entrepreneur=request.user).order_by('-created_at')
    rounds = annotate_percent_raised(rounds)
    return render(request, 'Investors/startup_dashboard.html', {'rounds': rounds, 'user': request.user})

@login_required
def investor_dashboard_offers(request):
    if request.user.role != 'investor':
        return redirect('home')
    commitments = InvestmentCommitment.objects.filter(investor=request.user).select_related('funding_round').order_by('-committed_at')
    for c in commitments:
        fr = c.funding_round
        c.funding_round.percent_raised = float(fr.total_committed()) / float(fr.target_goal) * 100 if fr.target_goal else 0
    return render(request, 'Investors/investor_dashboard_offers.html', {'commitments': commitments, 'user': request.user})


# Notification Views
@login_required
def notifications_list(request):
    """Display user's notifications"""
    notifications = NotificationService.get_user_notifications(request.user, limit=100)
    unread_count = NotificationService.get_unread_count(request.user)
    
    return render(request, 'Investors/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'user': request.user
    })

@login_required
@require_POST
def mark_notification_read(request):
    """Mark a specific notification as read"""
    notification_id = request.POST.get('notification_id')
    if not notification_id:
        return JsonResponse({'success': False, 'error': 'Missing notification_id'}, status=400)
    
    success = NotificationService.mark_as_read(notification_id, request.user)
    if success:
        unread_count = NotificationService.get_unread_count(request.user)
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })
    else:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)

@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    NotificationService.mark_all_as_read(request.user)
    return JsonResponse({'success': True, 'unread_count': 0})

@login_required
def get_unread_count(request):
    """Get unread notification count for AJAX requests"""
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({'count': count})

@login_required
def get_notifications_data(request):
    """Get notifications data for AJAX requests"""
    notifications = NotificationService.get_user_notifications(request.user, limit=20)
    unread_count = NotificationService.get_unread_count(request.user)
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'sender_name': notification.sender.get_full_name() if notification.sender else None,
            'time_ago': notification.time_ago,
            'is_read': notification.is_read,
            'related_object_id': notification.related_object_id,
            'related_object_type': notification.related_object_type,
        })
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })

@login_required
def test_investor_notification(request):
    if request.user.role == 'investor':
        from .services import NotificationService
        NotificationService.create_notification(
            recipient=request.user,
            notification_type='test',
            title='Test Notification',
            message='This is a test notification for an investor.'
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Not an investor'})

@login_required
def test_notification_redirect(request):
    """Test view to verify notification redirect logic"""
    user_id = request.GET.get('user_id', '6')
    current_user_role = request.user.role
    
    # This is the same logic as in the notification template
    messages_url = '/investor/messages/' if current_user_role == 'investor' else '/entrepreneur/messages/'
    redirect_url = f"{messages_url}?open_chat={user_id}"
    
    return JsonResponse({
        'current_user_role': current_user_role,
        'user_id': user_id,
        'messages_url': messages_url,
        'redirect_url': redirect_url,
        'expected_behavior': 'Should redirect to messages page with open_chat parameter'
    })

def search_users(request):
    """Search users by name, email, or role"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'users': [], 'total': 0})
    
    # Search in User model (removed username since it doesn't exist)
    users = User.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) | 
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:5]
    
    results = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.get_full_name() or user.email,
            'email': user.email,
            'role': user.role,
            'profile_url': f'/{user.role}/profile/{user.id}/' if user.role in ['investor', 'entrepreneur'] else '#'
        }
        results.append(user_data)
    
    return JsonResponse({
        'users': results,
        'total': len(results),
        'query': query
    })

def search_results_page(request):
    """Display full search results page"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('home')
    
    # Search in User model (removed username since it doesn't exist)
    users = User.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) | 
        Q(email__icontains=query)
    ).exclude(id=request.user.id)
    
    # Get profile images for users
    for user in users:
        try:
            if user.role == 'entrepreneur':
                profile = getattr(user, 'entrepreneur_profile', None)
                user.profile_image = profile.image if profile and profile.image else None
            elif user.role == 'investor':
                profile = getattr(user, 'investor_profile', None)
                user.profile_image = profile.image if profile and profile.image else None
            else:
                user.profile_image = None
        except Exception as e:
            print(f"Error getting profile image for user {user.id}: {e}")
            user.profile_image = None
    
    context = {
        'users': users,
        'query': query,
        'total_results': users.count()
    }
    
    return render(request, 'search_results.html', context)

@login_required
def portfolio_analytics(request):
    """Portfolio Analytics Dashboard for Investors"""
    if request.user.role != 'investor':
        messages.error(request, 'Access denied. You are not an investor.')
        return redirect('home')
    
    from django.db.models import Sum, Count, Avg
    from django.utils import timezone
    from datetime import timedelta
    import json
    
    # Get all investment commitments for the investor
    investments = InvestmentCommitment.objects.filter(
        investor=request.user
    ).select_related('funding_round', 'funding_round__startup')
    
    # Calculate key metrics
    total_invested = investments.aggregate(total=Sum('amount'))['total'] or 0
    active_investments = investments.filter(funding_round__status='active').count()
    successful_investments = investments.filter(funding_round__status='successful').count()
    
    # Calculate total equity across all investments
    total_equity = sum(inv.equity_share for inv in investments)
    
    # Calculate ROI (simplified - based on successful rounds)
    successful_amount = investments.filter(funding_round__status='successful').aggregate(total=Sum('amount'))['total'] or 0
    roi_percentage = ((successful_amount - total_invested) / total_invested * 100) if total_invested > 0 else 0.0
    
    # Risk level categorization
    early_stage_count = investments.filter(
        funding_round__startup__entrepreneur__entrepreneur_profile__company_stage__in=['idea', 'mvp', 'early']
    ).count()
    growth_stage_count = investments.filter(
        funding_round__startup__entrepreneur__entrepreneur_profile__company_stage__in=['growth', 'scale']
    ).count()
    
    # Funding round participation by type
    round_types = {}
    for inv in investments:
        round_name = inv.funding_round.round_name.lower()
        if 'seed' in round_name:
            round_types['seed'] = round_types.get('seed', 0) + 1
        elif 'series a' in round_name or 'seriesa' in round_name:
            round_types['series_a'] = round_types.get('series_a', 0) + 1
        elif 'series b' in round_name or 'seriesb' in round_name:
            round_types['series_b'] = round_types.get('series_b', 0) + 1
        elif 'series c' in round_name or 'seriesc' in round_name:
            round_types['series_c'] = round_types.get('series_c', 0) + 1
        else:
            round_types['other'] = round_types.get('other', 0) + 1
    
    # Portfolio growth over time (last 12 months)
    months = []
    monthly_totals = []
    for i in range(12):
        date = timezone.now() - timedelta(days=30*i)
        month_investments = investments.filter(committed_at__month=date.month, committed_at__year=date.year)
        month_total = month_investments.aggregate(total=Sum('amount'))['total'] or 0
        months.append(date.strftime('%b %Y'))
        monthly_totals.append(float(month_total))
    
    months.reverse()
    monthly_totals.reverse()
    
    # Top investments by amount
    top_investments = investments.order_by('-amount')[:5]
    
    # Industry distribution
    industry_distribution = {}
    for inv in investments:
        industry = inv.funding_round.startup.industry
        if industry in industry_distribution:
            industry_distribution[industry] += float(inv.amount)
        else:
            industry_distribution[industry] = float(inv.amount)
    
    # Convert to chart data
    industry_labels = list(industry_distribution.keys())
    industry_values = list(industry_distribution.values())
    months = months
    monthly_totals = monthly_totals
    round_types_table = list(round_types.items())
    industry_table = list(zip(industry_labels, industry_values))
    growth_table = list(zip(months, monthly_totals))
    context = {
        'total_invested': total_invested,
        'active_investments': active_investments,
        'successful_investments': successful_investments,
        'total_equity': total_equity,
        'early_stage_count': early_stage_count,
        'growth_stage_count': growth_stage_count,
        'round_types': round_types,
        'months': json.dumps(months),
        'monthly_totals': json.dumps(monthly_totals),
        'top_investments': top_investments,
        'industry_labels': json.dumps(industry_labels),
        'industry_values': json.dumps(industry_values),
        'roi_percentage': roi_percentage,
        'investments': investments,
        'industry_table': industry_table,
        'growth_table': growth_table,
        'round_types_table': round_types_table,
    }
    
    return render(request, 'Investors/portfolio_analytics.html', context)


@login_required
def user_network(request, user_id):
    """Display a specific user's network/followers"""
    from django.shortcuts import get_object_or_404
    from Entrepreneurs.models import User, Favorite
    
    target_user = get_object_or_404(User, id=user_id)
    
    # Check if the target user allows their network to be visible
    if not target_user.show_followers:
        context = {
            'target_user': target_user,
            'network_hidden': True,
        }
        return render(request, 'user_network.html', context)
    
    # Get the user's followers (people who follow this user)
    followers = []
    for favorite in Favorite.objects.filter(target_user=target_user).select_related('user', 'user__entrepreneur_profile', 'user__investor_profile'):
        if favorite.user.id != target_user.id:
            followers.append(favorite.user)
    
    # Get the user's following (people this user follows)
    following = []
    for favorite in Favorite.objects.filter(user=target_user).select_related('target_user', 'target_user__entrepreneur_profile', 'target_user__investor_profile'):
        if favorite.target_user.id != target_user.id:
            following.append(favorite.target_user)
    
    context = {
        'target_user': target_user,
        'followers': followers,
        'following': following,
        'network_hidden': False,
    }
    return render(request, 'user_network.html', context)

@login_required
def schedule_meeting(request, user_id):
    """Schedule a meeting with another user"""
    try:
        target_user = User.objects.get(id=user_id)
        if target_user == request.user:
            messages.error(request, "You cannot schedule a meeting with yourself.")
            return redirect('investors:profile', user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('home')
    
    if request.method == 'POST':
        form = MeetingRequestForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.organizer = request.user
            meeting.participant = target_user
            
            # Check for time conflicts
            from django.db.models import Q
            from datetime import timedelta
            
            meeting_start = meeting.datetime
            meeting_end = meeting.end_datetime
            
            # Check if there are any overlapping meetings for either user
            conflicting_meetings = Meeting.objects.filter(
                Q(organizer__in=[request.user, target_user]) | 
                Q(participant__in=[request.user, target_user])
            ).filter(
                Q(status='confirmed') | Q(status='pending')
            ).filter(
                Q(date=meeting.date) &
                Q(
                    Q(time__lt=meeting_end.time()) &
                    Q(time__gte=meeting_start.time())
                )
            )
            
            if conflicting_meetings.exists():
                messages.error(request, "There's a time conflict with an existing meeting.")
            else:
                meeting.save()
                
                # Create notification for the participant
                Notification.objects.create(
                    user=target_user,
                    sender=request.user,
                    notification_type='meeting',
                    title=f'Meeting Request from {request.user.get_full_name()}',
                    message=f'{request.user.get_full_name()} wants to meet with you on {meeting.date.strftime("%B %d")} at {meeting.time.strftime("%I:%M %p")}. Click to view and respond.',
                    related_object_id=meeting.id,
                    related_object_type='meeting'
                )
                
                messages.success(request, f"Meeting request sent to {target_user.get_full_name()}!")
                return redirect('entrepreneurs:meetings')
    else:
        form = MeetingRequestForm()
    
    context = {
        'form': form,
        'target_user': target_user,
    }
    return render(request, 'Investors/schedule_meeting.html', context)

@login_required
def meetings_list(request):
    """Display user's meetings (organized and participating)"""
    from django.utils import timezone
    today = timezone.now().date()
    
    # Get all meetings where user is organizer or participant
    all_meetings = Meeting.objects.filter(
        Q(organizer=request.user) | Q(participant=request.user)
    ).select_related('organizer', 'participant').order_by('date', 'time')
    
    # Separate meetings by status
    upcoming_meetings = all_meetings.filter(
        Q(date__gte=today) & Q(status='confirmed')
    )
    
    pending_meetings = all_meetings.filter(status='pending')
    
    # For pending meetings, show incoming requests first
    incoming_requests = pending_meetings.filter(participant=request.user)
    outgoing_requests = pending_meetings.filter(organizer=request.user)
    
    past_meetings = all_meetings.filter(
        Q(date__lt=today) | Q(status__in=['rejected', 'cancelled'])
    )
    
    context = {
        'upcoming_meetings': upcoming_meetings,
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
        'past_meetings': past_meetings,
        'today': today,
    }
    return render(request, 'Investors/meetings_list.html', context)

@login_required
def respond_to_meeting(request, meeting_id, action):
    """Accept or reject a meeting request"""
    try:
        # First, get the meeting regardless of status to show details
        meeting = Meeting.objects.get(id=meeting_id)
        
        # Check if user is the participant
        if meeting.participant != request.user:
            messages.error(request, "You can only respond to meeting requests sent to you.")
            return redirect('investors:meetings')
        
        # Check if meeting is still pending
        if meeting.status != 'pending':
            messages.warning(request, f"This meeting is already {meeting.status}. No action needed.")
            return redirect('investors:meetings')
            
    except Meeting.DoesNotExist:
        messages.error(request, "Meeting request not found.")
        return redirect('investors:meetings')
    
    if action == 'accept':
        meeting.status = 'confirmed'
        meeting.save()
        
        # Create notification for organizer
        Notification.objects.create(
            user=meeting.organizer,
            sender=request.user,
            notification_type='meeting',
            title=f'Meeting Accepted by {request.user.get_full_name()}',
            message=f'{request.user.get_full_name()} accepted your meeting request for {meeting.title} on {meeting.date.strftime("%B %d")}.',
            related_object_id=meeting.id,
            related_object_type='meeting'
        )
        
        messages.success(request, "Meeting accepted!")
        
    elif action == 'reject':
        meeting.status = 'rejected'
        meeting.save()
        
        # Create notification for organizer
        Notification.objects.create(
            user=meeting.organizer,
            sender=request.user,
            notification_type='meeting',
            title=f'Meeting Declined by {request.user.get_full_name()}',
            message=f'{request.user.get_full_name()} declined your meeting request for {meeting.title} on {meeting.date.strftime("%B %d")}.',
            related_object_id=meeting.id,
            related_object_type='meeting'
        )
        
        messages.info(request, "Meeting declined.")
    
    return redirect('investors:meetings')

@login_required
def cancel_meeting(request, meeting_id):
    """Cancel a confirmed meeting"""
    try:
        meeting = Meeting.objects.get(
            id=meeting_id, 
            organizer=request.user, 
            status='confirmed'
        )
    except Meeting.DoesNotExist:
        messages.error(request, "Meeting not found or you cannot cancel it.")
        return redirect('investors:meetings')
    
    if request.method == 'POST':
        meeting.status = 'cancelled'
        meeting.save()
        
        # Create notification for participant
        Notification.objects.create(
            user=meeting.participant,
            sender=request.user,
            notification_type='meeting',
            title=f'Meeting Cancelled by {request.user.get_full_name()}',
            message=f'{request.user.get_full_name()} cancelled the meeting "{meeting.title}" scheduled for {meeting.date.strftime("%B %d")}.',
            related_object_id=meeting.id,
            related_object_type='meeting'
        )
        
        messages.success(request, "Meeting cancelled successfully.")
        return redirect('investors:meetings')
    
    context = {'meeting': meeting}
    return render(request, 'Investors/cancel_meeting_confirm.html', context)

@login_required
def meeting_calendar(request):
    """Display meetings in a calendar view"""
    from django.utils import timezone
    from datetime import datetime, timedelta
    import calendar
    
    # Get current month
    now = timezone.now()
    year = request.GET.get('year', now.year)
    month = request.GET.get('month', now.month)
    
    try:
        year, month = int(year), int(month)
    except ValueError:
        year, month = now.year, now.month
    
    # Create calendar
    cal = calendar.monthcalendar(year, month)
    
    # Get meetings for this month
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date()
    else:
        end_date = datetime(year, month + 1, 1).date()
    
    meetings = Meeting.objects.filter(
        Q(organizer=request.user) | Q(participant=request.user)
    ).filter(
        date__gte=start_date,
        date__lt=end_date
    ).select_related('organizer', 'participant')
    
    # Organize meetings by date
    meetings_by_date = {}
    for meeting in meetings:
        date_key = meeting.date.isoformat()
        if date_key not in meetings_by_date:
            meetings_by_date[date_key] = []
        meetings_by_date[date_key].append(meeting)
    
    # Navigation
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'calendar': cal,
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'meetings_by_date': meetings_by_date,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': now.date(),
    }
    return render(request, 'Investors/meeting_calendar.html', context)

# OAuth Signal Handler
@receiver(user_signed_up)
def handle_investor_oauth_signup(sender, request, user, **kwargs):
    """Handle OAuth signup for investors"""
    try:
        if user.role == 'investor':
            # Create investor profile if it doesn't exist
            InvestorProfile.objects.get_or_create(user=user)
        elif user.role == 'entrepreneur':
            # Create entrepreneur profile if it doesn't exist
            from Entrepreneurs.models import EntrepreneurProfile
            EntrepreneurProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_stage': 'idea',
                    'team_size': '1',
                    'funding_raised': 'no_funding'
                }
            )
    except Exception as e:
        # Log the error but don't break the registration process
        print(f"Error in Investor OAuth signal handler: {e}")
        pass

def oauth_callback(request):
    """Handle OAuth callback and role selection for new investors"""
    if request.user.is_authenticated:
        # User is already authenticated, redirect to appropriate dashboard
        if request.user.role == 'entrepreneur':
            return redirect('entrepreneurs:dashboard')
        elif request.user.role == 'investor':
            return redirect('investors:dashboard')
        else:
            # User has no role, redirect to role selection
            return redirect('investors:role_selection')
    
    # If not authenticated, redirect to login
    return redirect('investors:login')

def role_selection(request):
    """Allow OAuth users to select their role"""
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['entrepreneur', 'investor']:
            request.user.role = role
            request.user.save()
            
            # Create appropriate profile
            if role == 'entrepreneur':
                from Entrepreneurs.models import EntrepreneurProfile
                EntrepreneurProfile.objects.get_or_create(
                    user=request.user,
                    defaults={
                        'company_stage': 'idea',
                        'team_size': '1',
                        'funding_raised': 'no_funding'
                    }
                )
                messages.success(request, 'Welcome to CoFound as an Entrepreneur!')
                return redirect('entrepreneurs:dashboard')
            else:
                InvestorProfile.objects.get_or_create(user=request.user)
                messages.success(request, 'Welcome to CoFound as an Investor!')
                return redirect('investors:dashboard')
    
    return render(request, 'Investors/role_selection.html')


