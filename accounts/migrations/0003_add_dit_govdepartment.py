# Generated by Django 3.2.2 on 2021-05-28 10:37

from django.db import migrations

"""
Data migration to add the DIT government department and its domains
"""


def add_dit_govdepartment(apps, schema_editor):
    GovDepartment = apps.get_model("accounts", "GovDepartment")
    GovDepartment.objects.update_or_create(
        name="DIT", email_domains=["trade.gov.uk", "digital.trade.gov.uk"]
    )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_auto_20210414_0914"),
    ]

    operations = [
        migrations.RunPython(add_dit_govdepartment),
    ]
