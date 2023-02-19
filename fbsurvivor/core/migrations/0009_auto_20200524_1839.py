# Generated by Django 3.0.6 on 2020-05-25 01:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_auto_20200524_1717"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="pick",
            index=models.Index(
                fields=["player", "week"], name="core_pick_player__7ddd2d_idx"
            ),
        ),
    ]
