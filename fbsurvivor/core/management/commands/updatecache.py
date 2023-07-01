from django.core.management.base import BaseCommand

from fbsurvivor.core.helpers import update_league_caches


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        update_league_caches()
        print("\n\nCleared Updated!\n\n")