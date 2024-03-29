# Generated by Django 3.2.4 on 2021-09-21 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0033_merge_20210921_0802"),
    ]

    operations = [
        migrations.AlterField(
            model_name="maturityselfassessment",
            name="gsc_last_changed_by",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The entity responsible for the most recent change",
                max_length=64,
                verbose_name="last updated by",
            ),
        ),
        migrations.AlterField(
            model_name="maturityselfassessment",
            name="gsc_review_on",
            field=models.DateField(
                blank=True,
                help_text="The date when a review should be carried out",
                null=True,
                verbose_name="review on",
            ),
        ),
        migrations.AlterField(
            model_name="maturityselfassessment",
            name="gsc_updated_on",
            field=models.DateField(
                blank=True,
                help_text="The date of the most recent change",
                null=True,
                verbose_name="last updated",
            ),
        ),
        migrations.AlterField(
            model_name="scenarioassessment",
            name="gsc_last_changed_by",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The entity responsible for the most recent change",
                max_length=64,
                verbose_name="last updated by",
            ),
        ),
        migrations.AlterField(
            model_name="scenarioassessment",
            name="gsc_review_on",
            field=models.DateField(
                blank=True,
                help_text="The date when a review should be carried out",
                null=True,
                verbose_name="review on",
            ),
        ),
        migrations.AlterField(
            model_name="scenarioassessment",
            name="gsc_updated_on",
            field=models.DateField(
                blank=True,
                help_text="The date of the most recent change",
                null=True,
                verbose_name="last updated",
            ),
        ),
        migrations.AlterField(
            model_name="supplychainstage",
            name="gsc_last_changed_by",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The entity responsible for the most recent change",
                max_length=64,
                verbose_name="last updated by",
            ),
        ),
        migrations.AlterField(
            model_name="supplychainstage",
            name="gsc_review_on",
            field=models.DateField(
                blank=True,
                help_text="The date when a review should be carried out",
                null=True,
                verbose_name="review on",
            ),
        ),
        migrations.AlterField(
            model_name="supplychainstage",
            name="gsc_updated_on",
            field=models.DateField(
                blank=True,
                help_text="The date of the most recent change",
                null=True,
                verbose_name="last updated",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="gsc_last_changed_by",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The entity responsible for the most recent change",
                max_length=64,
                verbose_name="last updated by",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="gsc_review_on",
            field=models.DateField(
                blank=True,
                help_text="The date when a review should be carried out",
                null=True,
                verbose_name="review on",
            ),
        ),
        migrations.AlterField(
            model_name="vulnerabilityassessment",
            name="gsc_updated_on",
            field=models.DateField(
                blank=True,
                help_text="The date of the most recent change",
                null=True,
                verbose_name="last updated",
            ),
        ),
    ]
