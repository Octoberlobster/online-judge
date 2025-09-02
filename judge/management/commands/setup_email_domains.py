from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from judge.models import AllowedEmailDomain


class Command(BaseCommand):
    help = 'Initialize default allowed email domains for registration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            action='append',
            help='Add specific domain(s) to allow (can be used multiple times)',
        )
        parser.add_argument(
            '--default',
            action='store_true',
            help='Add default edu.tw domain',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing allowed domains before adding new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = AllowedEmailDomain.objects.count()
            AllowedEmailDomain.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Cleared {count} existing allowed domains.')
            )

        domains_to_add = []
        
        # Add default domain if requested
        if options['default']:
            domains_to_add.append(('edu.tw', 'Taiwan educational institutions'))
        
        # Add custom domains if provided
        if options['domain']:
            for domain in options['domain']:
                domains_to_add.append((domain.lower(), f'Custom domain: {domain}'))

        # If no specific domains provided and not clearing, add default
        if not domains_to_add and not options['clear']:
            domains_to_add.append(('edu.tw', 'Taiwan educational institutions'))

        created_count = 0
        for domain, description in domains_to_add:
            domain_obj, created = AllowedEmailDomain.objects.get_or_create(
                domain=domain,
                defaults={
                    'description': description,
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created allowed domain: {domain}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Domain already exists: {domain}')
                )

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} new allowed domain(s).')
            )
        
        # Show current status
        total_domains = AllowedEmailDomain.objects.count()
        active_domains = AllowedEmailDomain.objects.filter(is_active=True).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCurrent status: {total_domains} total domains, {active_domains} active domains'
            )
        )
        
        if active_domains > 0:
            self.stdout.write('\nActive domains:')
            for domain in AllowedEmailDomain.objects.filter(is_active=True):
                self.stdout.write(f'  - {domain.domain} ({domain.description})')
