import datetime

import pytz
from django.test import TestCase

from fbsurvivor.core.models import Player, Season, Week, Team, Pick, PlayerStatus


class ModelTest(TestCase):
    def setUp(self) -> None:
        pst = pytz.timezone("US/Pacific")

        self.player = Player.objects.create(
            username="WickedUser",
            link="wickedgoodlink",
            email="test@test.com",
            phone="+10000000000",
            is_admin=True,
            is_email_confirmed=True,
            is_phone_confirmed=False,
        )

        self.season = Season.objects.create(year=2020, is_locked=True, is_current=True)

        self.week = Week.objects.create(
            season=self.season,
            week_num=1,
            lock_datetime=pst.localize(datetime.datetime(2020, 4, 1)),
        )

        self.team = Team.objects.create(season=self.season, team_code="NE", bye_week=5,)

        self.pick = Pick.objects.create(
            player=self.player, week=self.week, team=self.team,
        )

        self.player_status = PlayerStatus.objects.create(
            player=self.player,
            season=self.season,
            is_paid=True,
            is_retired=False,
            is_survivor=False,
            win_count=0,
            loss_count=0,
        )

    def test_add_to_win_count(self):
        self.pick.result = "W"
        self.pick.save()

        self.player_status.refresh_from_db()
        self.assertEqual(self.player_status.win_count, 1)

    def test_add_to_loss_count(self):
        self.pick.result = "L"
        self.pick.save()

        self.player_status.refresh_from_db()
        self.assertEqual(self.player_status.loss_count, 1)

    def test_switch_win_to_loss(self):
        self.pick.result = "W"
        self.pick.save()

        self.pick.result = "L"
        self.pick.save()

        self.player_status.refresh_from_db()

        self.assertEqual(self.player_status.win_count, 0)
        self.assertEqual(self.player_status.loss_count, 1)

    def test_switch_loss_to_win(self):
        self.pick.result = "L"
        self.pick.save()

        self.pick.result = "W"
        self.pick.save()

        self.player_status.refresh_from_db()

        self.assertEqual(self.player_status.win_count, 1)
        self.assertEqual(self.player_status.loss_count, 0)
