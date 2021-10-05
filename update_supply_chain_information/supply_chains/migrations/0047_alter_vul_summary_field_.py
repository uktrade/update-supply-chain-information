# Generated by Django 3.2.4 on 2021-10-05 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0046_vul_include_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="deliver_stage_summary_14",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Deliver stage 14 - Ability to ramp up UK delivery capacity - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="make_stage_summary_10",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Make stage 10 - Susceptibility to labour shortage\u200b - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="make_stage_summary_7",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Make stage 7 - Ability to\u200b substitute planned replacement - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="make_stage_summary_8",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Make stage 8 - Dependence on foreign contractors\u200b - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="make_stage_summary_9",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Make stage 9 - Ability to ramp up UK production capacity - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="receive_stage_summary_4",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Receive stage 4 - Reliance on long shipping lead times - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="receive_stage_summary_5",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Receive stage 5 - Susceptibility to port congestion - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="receive_stage_summary_6",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Receive stage 6 - Size of product stockpile held in UK - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="store_stage_summary_11",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Store stage 11 - Size of stock buffer held in UK\u200b - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="store_stage_summary_12",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Store stage 12 - Feasibility of stockpiling\u200b - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="store_stage_summary_13",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Store stage 13 - Availability of storage in UK\u200b - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="supply_stage_summary_1",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Supply stage 1 - Dependence on foreign suppliers for product - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="supply_stage_summary_2",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Supply stage 2 - Ability to source\xa0alternative\u200b products - Summary",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="supply_stage_summary_3",
            field=models.TextField(
                default="",
                help_text="Summary of supply stage.",
                verbose_name="Supply stage 3 - Resilience of\u200b supply base - Summary",
            ),
        ),
    ]
