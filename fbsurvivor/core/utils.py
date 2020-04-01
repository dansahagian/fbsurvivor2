from fbsurvivor.core.models import Season


def get_current_season():
    return Season.objects.get(is_current=True)
