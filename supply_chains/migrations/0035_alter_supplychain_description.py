# Generated by Django 3.2.4 on 2021-09-21 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0034_update_gsc_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="supplychain",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
    ]
