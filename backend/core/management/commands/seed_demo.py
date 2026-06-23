from django.core.management.base import BaseCommand

from core.services import seed_demo_products


class Command(BaseCommand):
    help = "Seed demo financial products for local screenshots."

    def handle(self, *args, **options):
        seed_demo_products()
        self.stdout.write(self.style.SUCCESS("Demo products created."))
