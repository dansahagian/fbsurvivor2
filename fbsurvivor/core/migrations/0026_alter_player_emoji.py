# Generated by Django 3.2.8 on 2021-11-21 21:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0025_player_emoji"),
    ]

    operations = [
        migrations.AlterField(
            model_name="player",
            name="emoji",
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
    ]
