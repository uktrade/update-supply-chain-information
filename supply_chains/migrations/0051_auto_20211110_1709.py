# Generated by Django 3.2.5 on 2021-11-10 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0050_auto_20211021_1018"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vulassessmentsupplystage",
            name="supply_rag_rating_2",
            field=models.CharField(
                choices=[
                    ("RED", "Red"),
                    ("AMBER", "Amber"),
                    ("GREEN", "Green"),
                    ("None", "—"),
                ],
                default="None",
                max_length=5,
                verbose_name="Supply stage 2 - Ability to source alternative products - RAG Rating",
            ),
        ),
        migrations.AlterField(
            model_name="vulassessmentsupplystage",
            name="supply_stage_rationale_2",
            field=models.TextField(
                default="",
                help_text="Rationale of supply stage.",
                verbose_name="Supply stage 2 - Ability to source alternative products - Rationale",
            ),
        ),
        migrations.AlterField(
            model_name="vulassessmentsupplystage",
            name="supply_stage_summary_2",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Supply stage 2 - Ability to source alternative products - Summary",
            ),
        ),
    ]
