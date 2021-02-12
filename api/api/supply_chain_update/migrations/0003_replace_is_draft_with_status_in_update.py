# Generated by Django 3.1.5 on 2021-02-12 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chain_update", "0002_rename_monthly_update_model"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="strategicactionupdate",
            name="is_draft",
        ),
        migrations.AddField(
            model_name="strategicactionupdate",
            name="status",
            field=models.CharField(
                choices=[
                    ("in_progress", "In progress"),
                    ("completed", "Completed"),
                    ("submitted", "Submitted"),
                ],
                default="in_progress",
                help_text="The 'completed' and 'in_progress' statuses are used to help\n users know whether they have completed all required fields for an update.\n The 'submitted' status refers to when a user can no longer edit an update.",
                max_length=11,
            ),
        ),
    ]
