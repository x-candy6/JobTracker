# Generated by Django 4.2.4 on 2023-08-23 00:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="distance",
            field=models.IntegerField(blank=True, max_length=100, null=True),
        ),
    ]
