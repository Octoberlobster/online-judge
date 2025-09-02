from django.core.management.base import BaseCommand
from django.db import models
from django.utils.translation import gettext as _
from judge.models import NavigationBar


class Command(BaseCommand):
    help = 'Add email domain management navigation item for administrators'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remove',
            action='store_true',
            help='Remove the email domain navigation item',
        )

    def handle(self, *args, **options):
        nav_key = 'email-domains'
        
        if options['remove']:
            try:
                nav_item = NavigationBar.objects.get(key=nav_key)
                nav_item.delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully removed navigation item: {nav_key}')
                )
            except NavigationBar.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Navigation item not found: {nav_key}')
                )
            return

        # Check if navigation item already exists
        if NavigationBar.objects.filter(key=nav_key).exists():
            self.stdout.write(
                self.style.WARNING(f'Navigation item already exists: {nav_key}')
            )
            return

        # Find the highest order number
        max_order = NavigationBar.objects.aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0

        # Create the navigation item
        nav_item = NavigationBar.objects.create(
            key=nav_key,
            label='Email Domains',  # Will be translatable
            path='/admin/judge/allowedemaildomain/',
            regex=r'^/admin/judge/allowedemaildomain/',
            order=max_order + 1
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created navigation item: {nav_item.key} -> {nav_item.path}'
            )
        )
        
        self.stdout.write(
            self.style.WARNING(
                'Note: This navigation item will be visible to all users. '
                'Consider adding permission checks in the template if needed.'
            )
        )
