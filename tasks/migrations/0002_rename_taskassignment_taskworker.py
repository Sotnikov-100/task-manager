# Generated by Django 5.1.7 on 2025-04-18 07:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="TaskAssignment",
            new_name="TaskWorker",
        ),
    ]
