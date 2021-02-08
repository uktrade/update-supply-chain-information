from api.accounts.models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from api.accounts.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset that returns all users.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
