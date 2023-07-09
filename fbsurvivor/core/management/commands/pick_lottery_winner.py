from secrets import choice

from django.core.management.base import BaseCommand

from fbsurvivor.core.models import Player, Season


class Command(BaseCommand):
    help = "Pick the winner of free entry for next season"

    def handle(self, *args, **options):
        current_season = Season.objects.get(is_current=True)

        # filter out players who retired, won survivor, and me
        players = Player.objects.filter(
            playerstatus__season=current_season,
            playerstatus__is_retired=False,
            playerstatus__is_survivor=False,
        ).exclude(username="DanTheAutomator")

        # filter out players who missed picks during the season
        ep = [
            p.username
            for p in players
            if not p.pick_set.filter(team__isnull=True, week__season=current_season)
            and sum(p.payout_set.filter(season=current_season).values_list("amount", flat=True))
            < 30
        ]
        display = "\n".join(ep)

        print(f"\n\nEligible Players:\n\n{display}\n\n")
        print(f"And the winner is... {choice(ep)}\n\n")
