# Generated by Django 3.2.8 on 2021-11-04 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fillup', '0004_fillup_addition_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='fillup',
            name='tank_full',
            field=models.BooleanField(default=True),
        ),
    ]
