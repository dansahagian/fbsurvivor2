# Generated by Django 3.1.3 on 2020-11-23 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_auto_20200908_1017"),
    ]

    operations = [
        migrations.AddField(
            model_name="player",
            name="notes",
            field=models.TextField(blank=True, null=True),
        ),
    ]