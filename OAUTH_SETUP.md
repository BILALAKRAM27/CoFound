# OAuth Authentication Setup Guide for CoFound

This guide will help you set up OAuth authentication for Google, LinkedIn, X (Twitter), and Apple in your CoFound Django project.

## Prerequisites

1. **Install Required Packages**
   ```bash
   pip install django-allauth==0.60.1 requests-oauthlib==1.3.1
   ```

2. **Database Migration**
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser (if not exists)**
   ```bash
   python manage.py createsuperuser
   ```

## OAuth Provider Setup

### 1. Google OAuth Setup

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select existing one

2. **Enable Google+ API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     ```
     http://localhost:8000/accounts/google/login/callback/
     http://127.0.0.1:8000/accounts/google/login/callback/
     ```

4. **Get Client ID and Secret**
   - Copy the Client ID and Client Secret

### 2. LinkedIn OAuth Setup

1. **Go to LinkedIn Developers**
   - Visit: https://www.linkedin.com/developers/
   - Sign in with your LinkedIn account

2. **Create App**
   - Click "Create App"
   - Fill in app details
   - Request access to "Sign In with LinkedIn"

3. **Get OAuth 2.0 Credentials**
   - Go to "Auth" tab
   - Add redirect URLs:
     ```
     http://localhost:8000/accounts/linkedin_oauth2/login/callback/
     http://127.0.0.1:8000/accounts/linkedin_oauth2/login/callback/
     ```
   - Copy Client ID and Client Secret

### 3. X (Twitter) OAuth Setup

1. **Go to Twitter Developer Portal**
   - Visit: https://developer.twitter.com/
   - Sign in and create a new app

2. **Configure App**
   - Go to "App settings" > "User authentication settings"
   - Enable OAuth 2.0
   - Set App permissions to "Read"
   - Add callback URLs:
     ```
     http://localhost:8000/accounts/twitter_oauth2/login/callback/
     http://127.0.0.1:8000/accounts/twitter_oauth2/login/callback/
     ```

3. **Get API Keys**
   - Copy API Key and API Secret Key

### 4. Apple OAuth Setup

1. **Go to Apple Developer Portal**
   - Visit: https://developer.apple.com/
   - Sign in with your Apple Developer account

2. **Create App ID**
   - Go to "Certificates, Identifiers & Profiles"
   - Create new App ID
   - Enable "Sign In with Apple"

3. **Create Service ID**
   - Create new Service ID
   - Configure "Sign In with Apple"
   - Add return URLs:
     ```
     http://localhost:8000/accounts/apple/login/callback/
     http://127.0.0.1:8000/accounts/apple/login/callback/
     ```

4. **Get Credentials**
   - Download private key
   - Note the Key ID and Team ID

## Django Admin Configuration

1. **Access Django Admin**
   - Go to: http://localhost:8000/admin/
   - Login with superuser credentials

2. **Add Sites**
   - Go to "Sites" > "Add site"
   - Domain: `localhost:8000`
   - Display name: `CoFound Local`

3. **Add Social Applications**
   - Go to "Social Applications" > "Add social application"
   - For each provider:

   **Google:**
   - Provider: `Google`
   - Name: `Google OAuth`
   - Client ID: [Your Google Client ID]
   - Secret Key: [Your Google Client Secret]
   - Sites: Add `localhost:8000`

   **LinkedIn:**
   - Provider: `LinkedIn OAuth2`
   - Name: `LinkedIn OAuth`
   - Client ID: [Your LinkedIn Client ID]
   - Secret Key: [Your LinkedIn Client Secret]
   - Sites: Add `localhost:8000`

   **Twitter:**
   - Provider: `Twitter OAuth2`
   - Name: `Twitter OAuth`
   - Client ID: [Your Twitter API Key]
   - Secret Key: [Your Twitter API Secret Key]
   - Sites: Add `localhost:8000`

   **Apple:**
   - Provider: `Apple`
   - Name: `Apple OAuth`
   - Client ID: [Your Apple Service ID]
   - Secret Key: [Your Apple Private Key content]
   - Sites: Add `localhost:8000`

## Environment Variables (Recommended)

Create a `.env` file in your project root:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# LinkedIn OAuth
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# Twitter OAuth
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret_key

# Apple OAuth
APPLE_CLIENT_ID=your_apple_service_id
APPLE_TEAM_ID=your_apple_team_id
APPLE_KEY_ID=your_apple_key_id
APPLE_PRIVATE_KEY=your_apple_private_key_content
```

## Testing OAuth

1. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

2. **Test Registration**
   - Go to: http://localhost:8000/entrepreneur/register/
   - Click on any OAuth button
   - Complete the OAuth flow
   - Select your role (Entrepreneur/Investor)

3. **Verify User Creation**
   - Check Django admin for new users
   - Verify profiles are created automatically

## Production Deployment

1. **Update Settings**
   - Change `ACCOUNT_DEFAULT_HTTP_PROTOCOL` to `'https'`
   - Set `DEBUG = False`
   - Update `ALLOWED_HOSTS`

2. **Update OAuth URLs**
   - Replace `localhost:8000` with your production domain
   - Update all callback URLs in OAuth provider settings

3. **Security Considerations**
   - Use environment variables for sensitive data
   - Enable HTTPS
   - Set up proper CORS if needed
   - Consider email verification

## Troubleshooting

### Common Issues

1. **"Social application matching query does not exist"**
   - Ensure you've added the social application in Django admin
   - Check that the provider name matches exactly

2. **"Invalid redirect URI"**
   - Verify callback URLs in OAuth provider settings
   - Check that your domain matches exactly

3. **"User already exists"**
   - Check if user with same email already exists
   - Consider implementing account linking

4. **"Permission denied"**
   - Verify OAuth app permissions
   - Check if required APIs are enabled

### Debug Mode

Enable debug logging in settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Support

If you encounter issues:

1. Check Django debug logs
2. Verify OAuth provider settings
3. Ensure all required packages are installed
4. Check database migrations are applied
5. Verify site configuration in Django admin

## Additional Resources

- [Django Allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [LinkedIn OAuth 2.0](https://developer.linkedin.com/docs/oauth2)
- [Twitter OAuth 2.0](https://developer.twitter.com/en/docs/authentication/oauth-2-0)
- [Apple Sign In](https://developer.apple.com/sign-in-with-apple/)
