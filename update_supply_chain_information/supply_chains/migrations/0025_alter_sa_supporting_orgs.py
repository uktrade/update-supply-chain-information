# Generated by Django 3.2.4 on 2021-09-06 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0024_add_action_gsc_notes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="strategicaction",
            name="supporting_organisations",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
