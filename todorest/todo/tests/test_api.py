import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from todo.models import Todo
from todo.serializers import TodoSerializer
from django.contrib.auth.models import User
import datetime
import pytz
from unittest import mock


class TodoApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(username='username1', password='password1')
        self.token1 = Token.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(username='username2', password='password2')
        self.token2 = Token.objects.create(user=self.user2)

        self.todo1 = Todo.objects.create(name='name1', owner=self.user1)
        self.todo2 = Todo.objects.create(name='name2', owner=self.user1)
        self.todo3 = Todo.objects.create(name='name3', owner=self.user1)

        self.todo4 = Todo.objects.create(name='name4', owner=self.user2)
        self.todo5 = Todo.objects.create(name='name5', owner=self.user2)

    def api_authentication(self, token):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_list(self):
        self.api_authentication(self.token1)

        url = reverse('todo_list')
        responce = self.client.get(url)

        todos = Todo.objects.filter(owner=self.user1)
        todos_serializer = TodoSerializer(todos, many=True).data

        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        self.assertEqual(todos_serializer, responce.data)

    def test_create_todo(self):
        self.api_authentication(self.token1)
        todos_count_before = Todo.objects.count()

        url = reverse('todo_list')
        data = {'name': 'new_name'}
        data_json = json.dumps(data)

        responce = self.client.post(url, data=data_json, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, responce.status_code)

        new_todo = Todo.objects.get(name='new_name')
        self.assertEqual(self.user1, new_todo.owner)

        todos_count_after = Todo.objects.count()
        self.assertEqual(todos_count_before + 1, todos_count_after)

    def test_retrieve_todo(self):
        self.api_authentication(self.token1)

        url = reverse('todo_rud', args=(self.todo1.id,))
        responce = self.client.get(url)

        todo = Todo.objects.get(id=self.todo1.id)
        todo_serialized = TodoSerializer(todo).data

        self.assertEqual(todo_serialized, responce.data)

    def test_update_todo(self):
        self.api_authentication(self.token1)

        url = reverse('todo_rud', args=(self.todo2.id,))
        data = {'name': 'new_name2',
                'done': True}
        data_json = json.dumps(data)
        responce = self.client.put(url, data=data_json, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, responce.status_code)
        todo2_new = Todo.objects.get(id=self.todo2.id)
        self.assertEqual('new_name2', todo2_new.name)
        self.assertEqual(True, todo2_new.done)

    def test_destroy_todo(self):
        self.api_authentication(self.token1)

        todos_count_before = Todo.objects.count()

        url = reverse('todo_rud', args=(self.todo3.id,))
        responce = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, responce.status_code)
        todos_count_after = Todo.objects.count()
        self.assertEqual(todos_count_before, todos_count_after + 1)
        self.assertFalse(Todo.objects.filter(id=self.todo3.id).exists())

    def test_retrieve_todo_not_owner(self):
        self.api_authentication(self.token1)

        url = reverse('todo_rud', args=(self.todo4.id,))
        responce = self.client.get(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, responce.status_code)

    def test_update_todo_not_owner(self):
        self.api_authentication(self.token1)

        url = reverse('todo_rud', args=(self.todo4.id,))
        data = {'name': 'new_name4',
                'done': True}
        data_json = json.dumps(data)
        responce = self.client.put(url, data=data_json, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, responce.status_code)
        todo4_new = Todo.objects.get(id=self.todo4.id)
        self.assertEqual(todo4_new, self.todo4)

    def test_destroy_todo_not_owner(self):
        self.api_authentication(self.token1)

        todos_count_before = Todo.objects.count()

        url = reverse('todo_rud', args=(self.todo4.id,))
        responce = self.client.delete(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, responce.status_code)
        todos_count_after = Todo.objects.count()
        self.assertEqual(todos_count_before, todos_count_after)
        self.assertTrue(Todo.objects.filter(id=self.todo3.id).exists())


class TodoApiFilterBackendsTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='username1', password='password1')

        mocked = datetime.datetime(2021, 12, 30, 0, 0, 0, tzinfo=pytz.utc)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            self.todo1 = Todo.objects.create(name='1_name', owner=self.user, done=True)

        mocked = datetime.datetime(2022, 1, 2, 12, 0, 0, tzinfo=pytz.utc)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            self.todo2 = Todo.objects.create(name='2_name', owner=self.user)

        mocked = datetime.datetime(2022, 1, 2, 22, 0, 0, tzinfo=pytz.utc)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            self.todo3 = Todo.objects.create(name='X_name', owner=self.user, done=True)

        mocked = datetime.datetime(2022, 6, 1, 22, 0, 0, tzinfo=pytz.utc)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=mocked)):
            self.todo4 = Todo.objects.create(name='A_name', owner=self.user)

    def test_ordering(self):
        test_cases = [{'ordering_type': 'date_created',
                       'expected_data': [self.todo1, self.todo2, self.todo3, self.todo4]},
                      {'ordering_type': '-date_created',
                       'expected_data': [self.todo4, self.todo3, self.todo2, self.todo1]},
                      {'ordering_type': 'name',
                       'expected_data': [self.todo1, self.todo2, self.todo4, self.todo3]},
                      {'ordering_type': '-name',
                       'expected_data': [self.todo3, self.todo4, self.todo2, self.todo1]},
                      ]

        url = reverse('todo_list')
        self.client.force_login(self.user)

        for test_case in test_cases:
            responce = self.client.get(url, data={'ordering': test_case['ordering_type']})
            expected_data = TodoSerializer(test_case['expected_data'], many=True).data
            self.assertEqual(expected_data, responce.data)

    def test_filter(self):
        test_cases = [{'filter_data': {'done': True},
                       'expected_data': [self.todo1, self.todo3]},
                      {'filter_data': {'done': False},
                       'expected_data': [self.todo2, self.todo4]},
                      {'filter_data': {'date_created__gte': datetime.datetime(2022, 1, 2, 22, 0, 0, tzinfo=pytz.utc)},
                                       'expected_data': [self.todo3, self.todo4]},
                      {'filter_data': {'date_created__gte': datetime.datetime(2022, 1, 2, 22, 0, 0, tzinfo=pytz.utc),
                                       'date_created__lte': datetime.datetime(2022, 1, 5, 00, 0, 0, tzinfo=pytz.utc)},
                       'expected_data': [self.todo3]}]

        url = reverse('todo_list')
        self.client.force_login(self.user)

        for test_case in test_cases:
            responce = self.client.get(url, data=test_case['filter_data'])
            expected_data = TodoSerializer(test_case['expected_data'], many=True).data
            self.assertEqual(expected_data, responce.data)
