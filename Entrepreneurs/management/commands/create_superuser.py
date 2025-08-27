from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with the custom User model'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True, help='Email address for the superuser')
        parser.add_argument('--first-name', type=str, required=True, help='First name for the superuser')
        parser.add_argument('--last-name', type=str, required=True, help='Last name for the superuser')
        parser.add_argument('--password', type=str, required=True, help='Password for the superuser')
        parser.add_argument('--role', type=str, choices=['entrepreneur', 'investor'], default='entrepreneur', help='Role for the superuser (default: entrepreneur)')

    def handle(self, *args, **options):
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        password = options['password']
        role = options['role']

        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User with email {email} already exists.')
                    )
                    return

                # Create superuser
                user = User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=role
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Superuser created successfully!\n'
                        f'Email: {email}\n'
                        f'Name: {first_name} {last_name}\n'
                        f'Role: {role}'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
