from django.contrib import admin

from fbsurvivor.core.models import (
    League,
    Player,
    PlayerStatus,
    Payout,
    Season,
    Week,
    Team,
    Lock,
    Pick,
)

admin.AdminSite.enable_nav_sidebar = False


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "is_admin",
        "has_email_reminders",
    ]

    def get_queryset(self, request):
        qs = super(PlayerAdmin, self).get_queryset(request)
        return qs.order_by("username")


@admin.register(PlayerStatus)
class PlayerStatusAdmin(admin.ModelAdmin):
    list_display = ["player", "season", "is_paid", "is_retired", "is_survivor"]
    list_editable = ["is_paid", "is_retired", "is_survivor"]
    list_filter = ["season"]

    def get_queryset(self, request):
        qs = super(PlayerStatusAdmin, self).get_queryset(request)
        return qs.order_by("player__username")


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ["year", "is_locked", "is_current"]
    list_editable = ["is_locked", "is_current"]


@admin.register(Week)
class WeekAdmin(admin.ModelAdmin):
    list_display = ["week_num", "season", "lock_datetime"]
    list_filter = ["season"]

    def get_queryset(self, request):
        qs = super(WeekAdmin, self).get_queryset(request)
        return qs.order_by("-season", "week_num")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["team_code", "season", "bye_week"]
    list_filter = ["season"]

    def get_queryset(self, request):
        qs = super(TeamAdmin, self).get_queryset(request)
        return qs.order_by("-season", "team_code")


@admin.register(Pick)
class PickAdmin(admin.ModelAdmin):
    list_display = ["week", "team", "player", "result"]
    list_editable = ["result"]
    list_filter = ["week__season", "player"]

    def get_queryset(self, request):
        qs = super(PickAdmin, self).get_queryset(request)
        return qs.order_by("-week__season", "-week__week_num")


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ["player", "season", "amount"]
    list_filter = ["season", "player"]

    def get_queryset(self, request):
        qs = super(PayoutAdmin, self).get_queryset(request)
        return qs.order_by("-season", "player")


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]


@admin.register(Lock)
class LockAdmin(admin.ModelAdmin):
    list_display = ["week", "team", "lock_datetime"]
