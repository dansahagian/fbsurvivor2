from fbsurvivor.core.models import PlayerStatus, Season


def update_player_records(year):
    try:
        season = Season.objects.get(year=year)
        player_statuses = PlayerStatus.objects.filter(season=season)
        updates = [ps.update_record() for ps in player_statuses]
        return len(updates)
    except Season.DoesNotExist:
        return 0
