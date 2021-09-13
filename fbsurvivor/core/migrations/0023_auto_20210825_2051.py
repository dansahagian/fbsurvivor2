# Generated by Django 3.2.4 on 2021-08-26 03:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_player_league"),
    ]

    operations = [
        migrations.CreateModel(
            name="League",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=12)),
                ("name", models.CharField(max_length=12)),
            ],
        ),
        migrations.DeleteModel(
            name="SignUpCode",
        ),
        migrations.RemoveField(
            model_name="player",
            name="league",
        ),
        migrations.AddField(
            model_name="player",
            name="league",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="core.league",
            ),
        ),
    ]