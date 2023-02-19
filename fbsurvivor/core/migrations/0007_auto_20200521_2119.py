# Generated by Django 3.0.6 on 2020-05-22 04:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_auto_20200517_1258_squashed_0008_auto_20200517_1403"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="playerstatus",
            index=models.Index(
                fields=["season"], name="core_player_season__627e82_idx"
            ),
        ),
    ]
