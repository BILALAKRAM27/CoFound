
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from Entrepreneurs.models import User
from .models import InvestorProfile, InvestorPortfolio, InvestmentDocument
from .forms import InvestorRegistrationForm, InvestorProfileForm
from django.http import JsonResponse
from Entrepreneurs.models import Post, PostMedia
from Entrepreneurs.forms import PostForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
from Entrepreneurs.models import Post, Comment
from Entrepreneurs.forms import CommentForm
from django.shortcuts import get_object_or_404
import base64


def investor_register(request):
    if request.method == 'POST':
        form = InvestorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'investor'
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create a basic profile with default values
            profile = InvestorProfile.objects.create(
                user=user,
                years_of_experience=0
            )
            
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to CoFound!')
            return redirect('home')  # Redirect to base.html (common home)
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
        from Entrepreneurs.models import EntrepreneurProfile
        profile = EntrepreneurProfile.objects.get_or_create(user=request.user)[0]

    # Get all users for the connections/network section
    users = User.objects.exclude(id=request.user.id).select_related(
        'entrepreneur_profile', 'investor_profile'
    )

    # Get all posts with media files, ordered by creation date
    try:
        from Entrepreneurs.models import Post
        posts = Post.objects.select_related(
            'author', 
            'author__entrepreneur_profile', 
            'author__investor_profile'
        ).prefetch_related(
            'media_files', 
            'likes', 
            'comments',
            'comments__author',
            'comments__author__entrepreneur_profile',
            'comments__author__investor_profile'
        ).order_by('-created_at')[:20]  # Show last 20 posts
    except Exception as e:
        print(f"Error fetching posts: {e}")
        posts = []

    context = {
        'profile': profile,
        'users': users,
        'posts': posts,
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


