from api.accounts.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "sso_email_user_id",
            "first_name",
            "last_name",
            "email",
            "gov_department",
        ]
        depth = 1
