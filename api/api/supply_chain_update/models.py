from django.db import models
from django.conf import settings
from api.accounts.models import GovDepartment
import uuid


class SupplyChain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH)
    last_submission_date = models.DateField(null=True)
    gov_department = models.ForeignKey(
        GovDepartment,
        on_delete=models.PROTECT,
        related_name="supply_chains",
    )


class StrategicAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=settings.CHARFIELD_MAX_LENGTH)
    start_date = models.DateField()
    description = models.TextField()
    is_archived = models.BooleanField()
    supply_chain = models.ForeignKey(
        SupplyChain,
        on_delete=models.PROTECT,
        related_name="strategic_actions",
    )


class StrategicActionUpdate(models.Model):
    IMPLEMENTATION_RAG_CHOICES = [
        ("RED", "Red"),
        ("AMBER", "Amber"),
        ("GREEN", "Green"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_draft = models.BooleanField(default=True)
    submission_date = models.DateField()
    content = models.TextField()
    implementation_rag_rating = models.CharField(
        max_length=5, choices=IMPLEMENTATION_RAG_CHOICES
    )
    reason_for_delays = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="monthly_updates",
    )
    strategic_action = models.ForeignKey(
        StrategicAction,
        on_delete=models.PROTECT,
        related_name="monthly_updates",
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        on_delete=models.PROTECT,
        related_name="monthly_updates",
    )
