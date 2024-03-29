# Generated by Django 3.2.4 on 2021-09-14 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0026_data_mig_on_0025"),
    ]

    operations = [
        migrations.AlterField(
            model_name="strategicaction",
            name="gsc_notes",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Free text area to record observations, notes by admin/gsc",
            ),
        ),
        migrations.AlterField(
            model_name="strategicaction",
            name="supporting_organisations",
            field=models.CharField(blank=True, default="", max_length=250),
        ),
        migrations.AlterField(
            model_name="supplychain",
            name="risk_severity_status",
            field=models.CharField(
                blank=True,
                choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
                default="",
                max_length=6,
            ),
        ),
    ]
