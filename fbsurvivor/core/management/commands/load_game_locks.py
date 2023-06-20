import arrow
from django.core.management.base import BaseCommand

from fbsurvivor.core.models.lock import Lock
from fbsurvivor.core.models.season import Season
from fbsurvivor.core.models.team import Team
from fbsurvivor.core.models.week import Week


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("year", type=int)
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        year = options["year"]
        filename = options["filename"]

        season = Season.objects.get(year=year)
        with open(filename, "r") as f:
            for line in f:
                week_num, team_code1, team_code2, lock_datetime = line.strip("/n").split(",")
                week = Week.objects.get(season=season, week_num=week_num)
                team1 = Team.objects.get(season=season, team_code=team_code1)
                team2 = Team.objects.get(season=season, team_code=team_code2)

                lock_datetime = arrow.get(lock_datetime).datetime

                Lock.objects.create(week=week, team=team1, lock_datetime=lock_datetime)
                Lock.objects.create(week=week, team=team2, lock_datetime=lock_datetime)

        print("Complete!")
