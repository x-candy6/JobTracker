# Generated by Django 4.2.4 on 2023-08-23 01:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ListingFeed", "0007_phraselist_user"),
    ]

    operations = [
        migrations.RenameField(
            model_name="phraselist",
            old_name="user",
            new_name="user_id",
        ),
    ]
