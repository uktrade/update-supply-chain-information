# Generated by Django 3.2.2 on 2021-05-12 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0009_auto_20210426_1251"),
    ]

    operations = [
        migrations.AlterField(
            model_name="strategicaction",
            name="start_date",
            field=models.DateField(null=True),
        ),
    ]
