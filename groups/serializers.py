from .models import HomeWork, Groups
from rest_framework import serializers


class GroupsSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d')

    class Meta:
        model = Groups
        fields = "__all__"
        depth = 1


class HomeWorkSerializer(serializers.ModelSerializer):
    begin_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d')
    end_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d')
    group = GroupsSerializer()

    class Meta:
        model = HomeWork
        fields = "__all__"
