# Generated by Django 3.0.5 on 2020-04-03 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_auto_20200402_0130"),
    ]

    operations = [
        migrations.AddField(
            model_name="playerstatus",
            name="loss_count",
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="playerstatus",
            name="win_count",
            field=models.SmallIntegerField(default=0),
        ),
    ]
