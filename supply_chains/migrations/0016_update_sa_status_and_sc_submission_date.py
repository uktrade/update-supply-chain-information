# Generated by Django 3.2.2 on 2021-05-25 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0015_sc_archived_reason"),
    ]

    operations = [
        migrations.AlterField(
            model_name="strategicactionupdate",
            name="status",
            field=models.CharField(
                choices=[
                    ("not_started", "Not started"),
                    ("in_progress", "In progress"),
                    ("ready_to_submit", "Ready to submit"),
                    ("submitted", "Submitted"),
                ],
                default="in_progress",
                help_text="The 'ready_to_submit' and 'in_progress' statuses are used to help\n users know whether they have completed all required fields for an update.\n The 'submitted' status refers to when a user can no longer edit an update.",
                max_length=15,
            ),
        ),
        migrations.AlterField(
            model_name="supplychain",
            name="last_submission_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
