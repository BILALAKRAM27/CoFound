from django import forms
from Entrepreneurs.models import User
from .models import InvestorProfile, InvestorPortfolio, InvestmentDocument, Meeting

# Message Settings Form
class MessageSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['message_privacy', 'show_followers']

# ---------------------------
# Registration / Profiles
# ---------------------------
class InvestorRegistrationForm(forms.ModelForm):
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


class InvestorProfileForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False, label="Email")
    image_upload = forms.FileField(required=False, label="Profile Image", widget=forms.FileInput(attrs={'accept': 'image/*'}))

    class Meta:
        model = InvestorProfile
        fields = [
            'email', 'firm_name', 'website', 'linkedin_url', 'bio', 'location',
            'investment_stage', 'investment_size', 'preferred_industries',
            'portfolio_companies', 'notable_exits'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tell us about your investment experience and interests...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/yourprofile'
            }),
            'investment_stage': forms.Select(attrs={
                'class': 'form-select'
            }),
            'investment_size': forms.Select(attrs={
                'class': 'form-select'
            }),
            'preferred_industries': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', 'Select preferred industries...'),
                ('ai', 'Artificial Intelligence (AI)'),
                ('fintech', 'Fintech'),
                ('healthtech', 'Healthtech'),
                ('enterprise_saas', 'Enterprise AI SaaS'),
                ('logistics', 'Logistics & Supply Chain Tech'),
                ('quantum', 'Quantum Computing'),
                ('insurtech', 'InsurTech'),
                ('spacetech', 'SpaceTech'),
                ('creator_tools', 'Creator Economy Tools'),
                ('cleantech', 'CleanTech & Green Energy'),
            ]),
            'portfolio_companies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List your current portfolio companies...'
            }),
            'notable_exits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List your notable exits and successful investments...'
            }),
            'firm_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your investment firm or company name'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourfirm.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def clean_firm_name(self):
        firm_name = self.cleaned_data.get('firm_name')
        qs = InvestorProfile.objects.filter(firm_name=firm_name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if firm_name and qs.exists():
            raise forms.ValidationError("Firm name must be unique.")
        return firm_name

    def clean_website(self):
        website = self.cleaned_data.get('website')
        qs = InvestorProfile.objects.filter(website=website)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if website and qs.exists():
            raise forms.ValidationError("Website must be unique.")
        return website

    def clean_linkedin_url(self):
        linkedin_url = self.cleaned_data.get('linkedin_url')
        qs = InvestorProfile.objects.filter(linkedin_url=linkedin_url)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if linkedin_url and qs.exists():
            raise forms.ValidationError("LinkedIn profile must be unique.")
        return linkedin_url


# ---------------------------
# Portfolio / Documents
# ---------------------------
class InvestorPortfolioForm(forms.ModelForm):
    class Meta:
        model = InvestorPortfolio
        fields = ['total_investments', 'number_of_investments', 'notable_exits']
        widgets = {
            'total_investments': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total amount invested across all deals'
            }),
            'number_of_investments': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Number of investments made'
            }),
            'notable_exits': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your notable exits or successful investments...'
            }),
        }


class InvestmentDocumentForm(forms.ModelForm):
    # Custom file field for document upload
    file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'investment_document'
        }),
        help_text='Upload a document (PDF, DOC, DOCX up to 10MB)'
    )
    
    class Meta:
        model = InvestmentDocument
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


# Post Form for social feed
class PostForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'What\'s on your mind? Share your startup journey, insights, or collaboration opportunities...'
        }),
        required=True
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
           
            'class': 'd-none',
            'accept': 'image/*'
        })
    )

class MeetingRequestForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'description', 'date', 'time', 'duration', 'location', 'meeting_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Meeting Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Meeting Description'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration': forms.Select(attrs={'class': 'form-control'}, choices=[
                (15, '15 minutes'),
                (30, '30 minutes'),
                (45, '45 minutes'),
                (60, '1 hour'),
                (90, '1.5 hours'),
                (120, '2 hours'),
            ]),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Meeting location or video call link'}),
            'meeting_type': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today
        from django.utils import timezone
        today = timezone.now().date()
        self.fields['date'].widget.attrs['min'] = today.isoformat()
