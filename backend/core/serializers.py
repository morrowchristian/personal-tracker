# backend/core/serializers.py
from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Task
        fields = [
            "id",
            "owner",
            "title",
            "description",
            "completed",
            "due_date",
            "priority",
            "created_at",
            "updated_at",
        ]
