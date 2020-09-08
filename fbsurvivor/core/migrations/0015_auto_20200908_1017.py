# Generated by Django 3.0.8 on 2020-09-08 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20200908_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pick',
            name='result',
            field=models.CharField(blank=True, choices=[('W', 'WIN'), ('L', 'LOSS'), ('R', 'RETIRED'), (None, 'None')], max_length=1, null=True),
        ),
    ]
