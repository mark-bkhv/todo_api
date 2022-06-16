from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):
    name = models.CharField('Name', max_length=128)
    date_created = models.DateTimeField('Date created', auto_now_add=True)
    done = models.BooleanField('Done', default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = ("Todo")
        verbose_name_plural = ("Todos")

    def __str__(self):
        return f'{self.owner.username} {self.name}'
