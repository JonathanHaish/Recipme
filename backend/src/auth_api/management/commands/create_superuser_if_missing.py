"""
Custom management command to create a superuser from environment variables.
Safe to run multiple times - only creates if user doesn't exist.

Usage:
    python manage.py create_superuser_if_missing

Environment variables:
    DJANGO_SUPERUSER_USERNAME - Admin username (default: admin)
    DJANGO_SUPERUSER_EMAIL    - Admin email (default: admin@recipme.com)
    DJANGO_SUPERUSER_PASSWORD - Admin password (required, no default for security)

Example in docker-compose.yml:
    environment:
      - DJANGO_SUPERUSER_USERNAME=admin
      - DJANGO_SUPERUSER_EMAIL=admin@recipme.com
      - DJANGO_SUPERUSER_PASSWORD=your-secure-password
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser from environment variables if one does not exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            help='Override DJANGO_SUPERUSER_USERNAME env var',
        )
        parser.add_argument(
            '--email',
            help='Override DJANGO_SUPERUSER_EMAIL env var',
        )
        parser.add_argument(
            '--password',
            help='Override DJANGO_SUPERUSER_PASSWORD env var',
        )

    def handle(self, *args, **options):
        username = options['username'] or os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
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

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" already exists. Skipping creation.')
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Superuser "{username}" created successfully.')
        )
