from django.core.management.base import BaseCommand, CommandError

from core.services import FinlifeAPIError, fetch_finlife_products


class Command(BaseCommand):
    help = "Load deposit and saving products from the Financial Supervisory Service API."

    def handle(self, *args, **options):
        try:
            deposit_count = fetch_finlife_products("deposit")
            saving_count = fetch_finlife_products("saving")
        except FinlifeAPIError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Loaded {deposit_count + saving_count} rate options."))
