# Generated by Django 4.2.4 on 2023-08-23 00:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("User", "0002_profile_distance"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="distance",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
