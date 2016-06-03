from django.db import models
from django.db.models.fields.related import ManyToManyField

class User(models.Model):
    name = models.TextField(primary_key=True, unique=True)

class Task(models.Model):
    id = models.TextField(primary_key=True, unique=True)
    name = models.TextField(db_index=True)
    finished = models.BooleanField(default=False)
    value = models.TextField(null=True)
    users = ManyToManyField(User)
    