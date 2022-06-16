from django.shortcuts import render

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from todo.models import Todo
from todo.serializers import TodoSerializer
from .permissions import UserIsOwnerTodo


class TodoListCreate(ListCreateAPIView):
    serializer_class = TodoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_fields = {
        'date_created': ['exact', 'gte', 'lte'],
        'done': ['exact']}
    ordering_fields = ['name', 'date_created']

    def get_queryset(self):
        return Todo.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TodoRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    queryset = Todo.objects.all()
    permission_classes = (UserIsOwnerTodo,)
