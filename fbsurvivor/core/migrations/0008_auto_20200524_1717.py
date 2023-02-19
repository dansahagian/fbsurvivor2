# Generated by Django 3.0.6 on 2020-05-25 00:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_auto_20200521_2119"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="playerstatus",
            name="core_player_season__627e82_idx",
        ),
        migrations.AddIndex(
            model_name="player",
            index=models.Index(fields=["link"], name="core_player_link_38fca8_idx"),
        ),
        migrations.AddIndex(
            model_name="playerstatus",
            index=models.Index(
                fields=["player", "season"], name="core_player_player__585e76_idx"
            ),
        ),
    ]
