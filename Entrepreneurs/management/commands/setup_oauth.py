from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Set up initial site configuration for OAuth authentication'

    def handle(self, *args, **options):
        # Create or update the default site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'localhost:8000',
                'name': 'CoFound Local'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created site: {site.domain} ({site.name})'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Site already exists: {site.domain} ({site.name})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                'OAuth site configuration is ready. '
                'Now add your OAuth applications in Django admin.'
            )
        )
