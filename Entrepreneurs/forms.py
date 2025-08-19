from django import forms
from .models import (
    User, EntrepreneurProfile, Startup, StartupDocument,
    Review, CollaborationRequest, Message, Notification,
    Favorite, ActivityLog, Post, Comment, PostMedia
)

# ---------------------------
# Registration / Profiles
# ---------------------------
class EntrepreneurRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'id': 'password'
        }),
        min_length=8,
        help_text='Password must be at least 8 characters long'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'confirm_password'
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'id': 'email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name',
                'id': 'first_name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name',
                'id': 'last_name'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        return cleaned_data


class EntrepreneurProfileForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False, label="Email")
    image_upload = forms.FileField(required=False, label="Profile Image", widget=forms.FileInput(attrs={'accept': 'image/*'}))

    class Meta:
        model = EntrepreneurProfile
        fields = [
            'email', 'company_name', 'website', 'linkedin_url', 'bio', 'location',
            'industries', 'startup_description', 'company_stage', 'funding_need', 'pitch_deck_url',
            'team_size', 'revenue', 'funding_raised', 'valuation'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us about yourself and your entrepreneurial journey...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your startup or company name'
            }),
            'industries': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Fintech, AI, Healthcare, SaaS'
            }),
            'startup_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your startup idea, product, or service...'
            }),
            'company_stage': forms.Select(attrs={
                'class': 'form-select'
            }),
            'funding_need': forms.Select(attrs={
                'class': 'form-select'
            }),
            'pitch_deck_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/pitch-deck.pdf'
            }),
            'team_size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'revenue': forms.Select(attrs={
                'class': 'form-select'
            }),
            'funding_raised': forms.Select(attrs={
                'class': 'form-select'
            }),
            'valuation': forms.Select(attrs={
                'class': 'form-select'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourstartup.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        qs = EntrepreneurProfile.objects.filter(company_name=company_name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if company_name and qs.exists():
            raise forms.ValidationError("Company name must be unique.")
        return company_name

    def clean_website(self):
        website = self.cleaned_data.get('website')
        qs = EntrepreneurProfile.objects.filter(website=website)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if website and qs.exists():
            raise forms.ValidationError("Website must be unique.")
        return website

    def clean_linkedin_url(self):
        linkedin_url = self.cleaned_data.get('linkedin_url')
        qs = EntrepreneurProfile.objects.filter(linkedin_url=linkedin_url)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if linkedin_url and qs.exists():
            raise forms.ValidationError("LinkedIn profile must be unique.")
        return linkedin_url


# ---------------------------
# Startups / Docs
# ---------------------------
class StartupForm(forms.ModelForm):
    # Custom logo field for file upload
    logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'startup_logo'
        }),
        help_text='Upload a startup logo (JPG, PNG, GIF up to 5MB)'
    )
    
    class Meta:
        model = Startup
        fields = ['name', 'description', 'industry', 'website', 'logo', 'funding_goal']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Startup name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your startup...'
            }),
            'industry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., FinTech, HealthTech, AI'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourstartup.com'
            }),
            'funding_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Funding goal amount'
            }),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            # Check file size (5MB limit)
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Logo file size must be under 5MB.")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if logo.content_type not in allowed_types:
                raise forms.ValidationError("Only JPG, PNG, and GIF images are allowed.")
        
        return logo


class StartupDocumentForm(forms.ModelForm):
    # Custom file field for document upload
    file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'startup_document'
        }),
        help_text='Upload a document (PDF, DOC, DOCX up to 10MB)'
    )
    
    class Meta:
        model = StartupDocument
        fields = ['title', 'file_name', 'file_type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document title'
            }),
            'file_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'File name'
            }),
            'file_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., application/pdf'
            }),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB.")
            
            # Check file type
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain'
            ]
            if file.content_type not in allowed_types:
                raise forms.ValidationError("Only PDF, DOC, DOCX, and TXT files are allowed.")
        
        return file


# ---------------------------
# Social / Collaboration
# ---------------------------
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['entrepreneur', 'rating', 'comment']
        widgets = {
            'entrepreneur': forms.Select(attrs={
                'class': 'form-select'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your experience...'
            }),
        }


class CollaborationRequestForm(forms.ModelForm):
    class Meta:
        model = CollaborationRequest
        fields = ['entrepreneur', 'message']
        widgets = {
            'entrepreneur': forms.Select(attrs={
                'class': 'form-select'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain why you want to collaborate...'
            }),
        }


class MessageForm(forms.ModelForm):
    # Add file field for attachments (optional)
    file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    message_type = forms.ChoiceField(choices=Message.MESSAGE_TYPES, initial='text', widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Message
        fields = ['receiver', 'content', 'file', 'message_type']
        widgets = {
            'receiver': forms.Select(attrs={
                'class': 'form-select'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message...'
            }),
        }


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Notification title'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notification message'
            }),
        }


class FavoriteForm(forms.ModelForm):
    class Meta:
        model = Favorite
        fields = ['target_user']
        widgets = {
            'target_user': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class ActivityLogForm(forms.ModelForm):
    class Meta:
        model = ActivityLog
        fields = ['action', 'details']
        widgets = {
            'action': forms.Select(attrs={
                'class': 'form-select'
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Additional details...'
            }),
        }


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '4',
            'placeholder': "What's on your mind? Share your startup journey, insights, or collaboration opportunities..."
        }),
        required=False  # Make content optional since we can have media-only posts
    )
    
    # Single file fields - multiple files will be handled in the view
    images = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control'
        }),
        label="Images"
    )
    
    videos = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'video/*',
            'class': 'form-control'
        }),
        label="Videos"
    )
    
    documents = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': '.pdf,.doc,.docx,.txt,.ppt,.pptx',
            'class': 'form-control'
        }),
        label="Documents"
    )

    class Meta:
        model = Post
        fields = ['content']


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Write a comment...',
            'maxlength': 500,
        }),
        label='',
        required=True
    )
    class Meta:
        model = Comment
        fields = ['content']
