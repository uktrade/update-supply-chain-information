# Generated by Django 3.2.2 on 2021-05-26 16:07

from django.db import migrations

"""
Data migration to add a HealthCheck object to the db.

This will enable a smoke test to check connection between the app
and db.
"""


def add_healthcheck_object(apps, schema_editor):
    HealthCheck = apps.get_model("healthcheck", "HealthCheck")
    h = HealthCheck(health_check_field=True)
    h.save()


class Migration(migrations.Migration):

    dependencies = [
        ("healthcheck", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_healthcheck_object),
    ]
