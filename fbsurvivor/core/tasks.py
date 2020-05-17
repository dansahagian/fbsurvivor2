from fbsurvivor.core.models import PlayerStatus, Season, Pick


def update_player_records(year):
    try:
        season = Season.objects.get(year=year)
        player_statuses = PlayerStatus.objects.filter(season=season)
        updates = [update_record(ps) for ps in player_statuses]
        return len(updates)
    except Season.DoesNotExist:
        return 0


def update_record(player_status):
    player = player_status.player
    season = player_status.season

    picks = Pick.objects.filter(player=player, week__season=season)
    player_status.win_count = picks.filter(result="W").count()
    player_status.loss_count = picks.filter(result="L").count()
    player_status.save()
    return True
