# Generated by Django 3.2.4 on 2021-09-23 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0038_merge_20210923_0945"),
    ]

    operations = [
        migrations.AlterField(
            model_name="supplychainstage",
            name="name",
            field=models.CharField(
                choices=[
                    ("demand requirements", "Demand Requirements"),
                    (
                        "raw materials extraction/mining",
                        "Raw Materials Extraction/Mining",
                    ),
                    ("refining", "Refining"),
                    (
                        "raw materials processing/refining",
                        "Raw Materials Processing/Refining",
                    ),
                    ("chemical processing", "Chemical Processing"),
                    (
                        "other material-conversion process",
                        "Other Material-Conversion Process",
                    ),
                    ("raw materials suppliers", "Raw Materials Suppliers"),
                    ("intermediate goods/capital", "Intermediate Goods/Capital"),
                    ("inbound logistics", "Inbound Logistics"),
                    ("delivery/shipping ", "Delivery/Shipping "),
                    ("manufacturing", "Manufacturing"),
                    ("component suppliers", "Component Suppliers"),
                    ("finished goods supplier", "Finished Goods Supplier"),
                    ("assembly", "Assembly"),
                    (
                        "testing/verification/approval/release",
                        "Testing/Verification/Approval/Release",
                    ),
                    ("finished product", "Finished Product"),
                    ("packaging/repackaging", "Packaging/Repackaging"),
                    ("outbound logistics", "Outbound Logistics"),
                    ("storage/store", "Storage/Store"),
                    ("distributors", "Distributors"),
                    (
                        "end point (retailer, hospital, grid, etc)",
                        "End Point (Retailer, Hospital, Grid, etc)",
                    ),
                    ("end use/consumer", "End Use/Consumer"),
                    ("service provider", "Service Provider"),
                    ("installation", "Installation"),
                    ("decommission  assets", "Decommission  Assets"),
                    ("recycling", "Recycling"),
                    ("waste disposal/asset disposal", "Waste Disposal/Asset Disposal"),
                    ("maintenance", "Maintenance"),
                    ("other - please describe", "Other - Please Describe"),
                ],
                default="",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="supplychainstagesection",
            name="name",
            field=models.CharField(
                choices=[
                    ("overview", "Overview"),
                    ("key products", "Key Products"),
                    ("key services", "Key Services"),
                    ("key activities", "Key Activities"),
                    ("key countries", "Key Countries"),
                    ("key transport links", "Key Transport Links"),
                    ("key companies", "Key Companies"),
                    ("key sectors", "Key Sectors"),
                    ("other relevant information", "Other Relevant Information"),
                ],
                default="",
                max_length=50,
            ),
        ),
    ]