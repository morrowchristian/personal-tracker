# backend/core/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task
from .serializers import TaskSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })


class PingView(APIView):
    def get(self, request):
        return Response({"ping": "pong"})


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD for the logged-in user's own tasks.

    The queryset is always scoped to request.user, so a user can
    never list, retrieve, update, or delete another user's tasks.
    """

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def toggle(self, request, pk=None):
        """Flip a task's completed flag."""
        task = self.get_object()
        task.completed = not task.completed
        task.save(update_fields=["completed", "updated_at"])
        return Response(self.get_serializer(task).data)
