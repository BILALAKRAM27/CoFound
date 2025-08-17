
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from Entrepreneurs.models import User
from .models import InvestorProfile, InvestorPortfolio, InvestmentDocument
from .forms import InvestorRegistrationForm, InvestorProfileForm


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
        'entrepreneurprofile', 'investorprofile'
    )

    # Import Post model and get sample posts (you'll need to create this model)
    try:
        from Entrepreneurs.models import Post
        posts = Post.objects.all().order_by('-created_at')[:10]
    except:
        # If Post model doesn't exist yet, create empty list
        posts = []

    # Create a simple form for post creation
    from .forms import PostForm
    form = PostForm()

    context = {
        'profile': profile,
        'users': users,
        'posts': posts,
        'form': form,
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


