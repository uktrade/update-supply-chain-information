# Generated by Django 3.2.4 on 2021-09-15 15:41

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("supply_chains", "0027_alter_sc_risk_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="SupplyChainStage",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("demand_requirements", "Demand Requirements"),
                            ("raw_material_ext", "Raw Materials Extraction/Mining"),
                            ("refining", "Refining"),
                            ("raw_material_proc", "Raw Materials Processing/Refining"),
                            ("chemical_processing", "Chemical Processing"),
                            (
                                "other_material_proc",
                                "Other Material-Conversion Process",
                            ),
                            ("raw_material_sup", "Raw Materials Suppliers"),
                            ("intermediate_goods", "Intermediate Goods/Capital"),
                            ("inbound_log", "Inbound Logistics"),
                            ("delivery", "Delivery/Shipping "),
                            ("manufacturing", "Manufacturing"),
                            ("comp_sup", "Component Suppliers"),
                            ("finished_goods_sup", "Finished Goods Supplier"),
                            ("assembly", "Assembly"),
                            ("testing_verif", "Testing/Verification/Approval/Release"),
                            ("finished_product", "Finished Product"),
                            ("packaging", "Packaging/Repackaging"),
                            ("outbound_log", "Outbound Logistics"),
                            ("storage", "Storage/Store"),
                            ("distributors", "Distributors"),
                            ("endpoint", "End Point (Retailer, Hospital, Grid, etc)"),
                            ("end_use", "End Use/Consumer"),
                            ("service_provider", "Service Provider"),
                            ("installation", "Installation"),
                            ("decommission", "Decommission  Assets"),
                            ("recycling", "Recycling"),
                            ("waste_disposal", "Waste Disposal/Asset Disposal"),
                            ("maintenance", "Maintenance"),
                            ("other", "Other - Please Describe"),
                        ],
                        default="",
                        max_length=50,
                    ),
                ),
                (
                    "order",
                    models.PositiveSmallIntegerField(
                        default="", help_text="Sequential order number of this stage"
                    ),
                ),
                (
                    "supply_chain",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="chain_stages",
                        to="supply_chains.supplychain",
                    ),
                ),
            ],
            options={
                "unique_together": {("supply_chain", "name")},
            },
        ),
        migrations.CreateModel(
            name="SupplyChainStageSection",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("overview", "Overview"),
                            ("key_products", "Key Products"),
                            ("key_services", "Key Services"),
                            ("key_activities", "Key Activities"),
                            ("key_countries", "Key Countries"),
                            ("key_transport_links", "Key Transport Links"),
                            ("key_companies", "Key Companies"),
                            ("key_sectors", "Key Sectors"),
                            ("other_info", "Other Relevant Information"),
                        ],
                        default="",
                        max_length=50,
                    ),
                ),
                ("description", models.TextField(default="")),
                (
                    "chain_stage",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="stage_sections",
                        to="supply_chains.supplychainstage",
                    ),
                ),
            ],
            options={
                "unique_together": {("chain_stage", "name")},
            },
        ),
    ]
