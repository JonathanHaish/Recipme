"""
Custom management command to create a superuser from environment variables.
Safe to run multiple times - only creates if user doesn't exist.

Usage:
    python manage.py create_superuser_if_missing

Environment variables:
    DJANGO_SUPERUSER_EMAIL    - Admin email (default: admin@recipme.com) - also used as username
    DJANGO_SUPERUSER_PASSWORD - Admin password (required, no default for security)

Note: Username will be set to the email address for consistency with the login system.

Example in .env file:
    DJANGO_SUPERUSER_EMAIL=admin@recipme.com
    DJANGO_SUPERUSER_PASSWORD=your-secure-password
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser from environment variables if one does not exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            help='Override DJANGO_SUPERUSER_EMAIL env var (also used as username)',
        )
        parser.add_argument(
            '--password',
            help='Override DJANGO_SUPERUSER_PASSWORD env var',
        )

    def handle(self, *args, **options):
        email = options['email'] or os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@recipme.com')
        password = options['password'] or os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stderr.write(
                self.style.WARNING(
                    'No password provided. Set DJANGO_SUPERUSER_PASSWORD env var or use --password flag.\n'
                    'Skipping superuser creation.'
                )
            )
            return

        # Use email as username for consistency with login system
        # This allows users to log in with their email address
        if User.objects.filter(username=email).exists():
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{email}" already exists. Skipping creation.')
            )
            return

        User.objects.create_superuser(
            username=email,  # Use email as username
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(f'Superuser "{email}" created successfully (username=email).')
        )
