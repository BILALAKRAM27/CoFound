from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.db import transaction

class Command(BaseCommand):
    help = 'Set up OAuth providers for social authentication'

    def add_arguments(self, parser):
        parser.add_argument('--google-client-id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--google-secret', type=str, help='Google OAuth Secret')
        parser.add_argument('--linkedin-client-id', type=str, help='LinkedIn OAuth Client ID')
        parser.add_argument('--linkedin-secret', type=str, help='LinkedIn OAuth Secret')
        parser.add_argument('--twitter-client-id', type=str, help='Twitter OAuth Client ID')
        parser.add_argument('--twitter-secret', type=str, help='Twitter OAuth Secret')
        parser.add_argument('--apple-client-id', type=str, help='Apple OAuth Client ID')
        parser.add_argument('--apple-secret', type=str, help='Apple OAuth Secret')

    def handle(self, *args, **options):
        try:
            # Get the site
            site = Site.objects.get(id=1)
            self.stdout.write(f'Using site: {site.domain} (ID: {site.id})')

            with transaction.atomic():
                # Google OAuth
                if options['google_client_id'] and options['google_secret']:
                    google_app, created = SocialApp.objects.get_or_create(
                        provider='google',
                        defaults={
                            'name': 'Google',
                            'client_id': options['google_client_id'],
                            'secret': options['google_secret'],
                        }
                    )
                    if created:
                        google_app.sites.add(site)
                        self.stdout.write(
                            self.style.SUCCESS('Google OAuth provider created successfully!')
                        )
                    else:
                        google_app.client_id = options['google_client_id']
                        google_app.secret = options['google_secret']
                        google_app.save()
                        self.stdout.write(
                            self.style.SUCCESS('Google OAuth provider updated successfully!')
                        )

                # LinkedIn OAuth
                if options['linkedin_client_id'] and options['linkedin_secret']:
                    linkedin_app, created = SocialApp.objects.get_or_create(
                        provider='linkedin_oauth2',
                        defaults={
                            'name': 'LinkedIn',
                            'client_id': options['linkedin_client_id'],
                            'secret': options['linkedin_secret'],
                        }
                    )
                    if created:
                        linkedin_app.sites.add(site)
                        self.stdout.write(
                            self.style.SUCCESS('LinkedIn OAuth provider created successfully!')
                        )
                    else:
                        linkedin_app.client_id = options['linkedin_client_id']
                        linkedin_app.secret = options['linkedin_secret']
                        linkedin_app.save()
                        self.stdout.write(
                            self.style.SUCCESS('LinkedIn OAuth provider updated successfully!')
                        )

                # Twitter OAuth
                if options['twitter_client_id'] and options['twitter_secret']:
                    twitter_app, created = SocialApp.objects.get_or_create(
                        provider='twitter_oauth2',
                        defaults={
                            'name': 'Twitter',
                            'client_id': options['twitter_client_id'],
                            'secret': options['twitter_secret'],
                        }
                    )
                    if created:
                        twitter_app.sites.add(site)
                        self.stdout.write(
                            self.style.SUCCESS('Twitter OAuth provider created successfully!')
                        )
                    else:
                        twitter_app.client_id = options['twitter_client_id']
                        twitter_app.secret = options['twitter_secret']
                        twitter_app.save()
                        self.stdout.write(
                            self.style.SUCCESS('Twitter OAuth provider updated successfully!')
                        )

                # Apple OAuth
                if options['apple_client_id'] and options['apple_secret']:
                    apple_app, created = SocialApp.objects.get_or_create(
                        provider='apple',
                        defaults={
                            'name': 'Apple',
                            'client_id': options['apple_client_id'],
                            'secret': options['apple_secret'],
                        }
                    )
                    if created:
                        apple_app.sites.add(site)
                        self.stdout.write(
                            self.style.SUCCESS('Apple OAuth provider created successfully!')
                        )
                    else:
                        apple_app.client_id = options['apple_client_id']
                        apple_app.secret = options['apple_secret']
                        apple_app.save()
                        self.stdout.write(
                            self.style.SUCCESS('Apple OAuth provider updated successfully!')
                        )

                # List all social apps
                apps = SocialApp.objects.all()
                self.stdout.write(f'\nTotal SocialApp objects: {apps.count()}')
                for app in apps:
                    self.stdout.write(f'- {app.name} ({app.provider})')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up OAuth providers: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
