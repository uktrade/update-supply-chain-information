# Generated by Django 3.2.5 on 2021-10-21 10:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0049_auto_20211020_1715"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="supplychaincriticality",
            options={"verbose_name_plural": "Criticality"},
        ),
        migrations.AlterModelOptions(
            name="supplychainmaturity",
            options={"verbose_name_plural": "Maturity"},
        ),
    ]
