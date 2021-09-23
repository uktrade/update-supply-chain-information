# Generated by Django 3.2.4 on 2021-09-22 08:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0036_auto_20210921_1240"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scenarioassessment",
            name="supply_chain",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="scenario_assessment",
                to="supply_chains.supplychain",
            ),
        ),
    ]
