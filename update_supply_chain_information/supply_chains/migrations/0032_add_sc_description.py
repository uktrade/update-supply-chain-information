# Generated by Django 3.2.4 on 2021-09-09 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0031_del_gsc_notes_from_stage_sections"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplychain",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]