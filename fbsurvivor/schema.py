import graphene
from graphene_django import DjangoObjectType

from fbsurvivor.core.models import Team, Season, PlayerStatus, Player, Pick


class TeamType(DjangoObjectType):
    class Meta:
        model = Team
        fields = ("id", "season", "team_code", "bye_week")


class SeasonType(DjangoObjectType):
    class Meta:
        model = Season


class PlayerType(DjangoObjectType):
    class Meta:
        model = Player
        fields = (
            "id",
            "username",
            "pick_set",
        )


class PickType(DjangoObjectType):
    class Meta:
        model = Pick


class PlayerStatusType(DjangoObjectType):
    class Meta:
        model = PlayerStatus


class Query(graphene.ObjectType):
    season = graphene.Field(SeasonType, year=graphene.Int(required=True))
    picks = graphene.List(
        PickType,
        player=graphene.Int(required=True),
        season=graphene.Int(required=True),
    )

    @staticmethod
    def resolve_season(root, info, year):
        return Season.objects.get(year=year)

    @staticmethod
    def resolve_picks(root, info, player, season):
        player = Player.objects.get(id=player)
        season = Season.objects.get(id=season)

        return Pick.objects.for_board(player=player, season=season)


schema = graphene.Schema(query=Query)
