# Generated by Django 3.0.5 on 2020-04-10 00:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_auto_20200403_0047"),
    ]

    operations = [
        migrations.AlterModelOptions(name="season", options={"ordering": ["-year"]},),
        migrations.AlterModelOptions(
            name="team", options={"ordering": ["-season", "team_code"]},
        ),
    ]