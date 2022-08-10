from django.contrib.auth.models import User
from rest_framework import serializers

from todo.models import Todo


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class TodoSerializer(serializers.ModelSerializer):
    owner = UserModelSerializer(read_only=True)
    class Meta:
        model = Todo
        fields = ['id','name', 'date_created', 'done', 'owner']
