from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class NoUsernameAccountAdapter(DefaultAccountAdapter):
    def clean_username(self, username, shallow=False):
        # Always return an empty string for username
        return ""

class NoUsernameSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # Ensure username is always blank
        if hasattr(user, 'username'):
            user.username = ""
        return user
    
    def get_signup_form_initial_data(self, sociallogin):
        # Return initial data without username
        initial = super().get_signup_form_initial_data(sociallogin)
        if 'username' in initial:
            del initial['username']
        return initial

class NoUsernameSignupForm(forms.Form):
    """Custom signup form without username field"""
    
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    password2 = forms.CharField(
        label="Confirm Password",
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8
    )
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, request):
        from allauth.account.utils import complete_signup
        from allauth.account import app_settings as allauth_settings
        
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1']
        )
        
        # Complete the signup process
        complete_signup(request, user, allauth_settings.EMAIL_VERIFICATION, None)
        return user

class NoUsernameSocialSignupForm(forms.Form):
    """Custom social signup form without username field"""
    
    def __init__(self, *args, **kwargs):
        self.sociallogin = kwargs.pop('sociallogin')
        super().__init__(*args, **kwargs)
    
    def save(self, request):
        user = self.sociallogin.user
        user.save()
        self.sociallogin.save(request)
        return user
    
    def try_save(self, request):
        """Required method for allauth SignupView"""
        user = self.save(request)
        return user, None  # Return (user, None) as expected by allauth
