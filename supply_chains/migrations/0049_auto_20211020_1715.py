# Generated by Django 3.2.5 on 2021-10-20 17:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0048_auto_20211020_1706"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="historicalsupplychain",
            name="criticality_rating",
        ),
        migrations.RemoveField(
            model_name="supplychain",
            name="criticality_rating",
        ),
    ]