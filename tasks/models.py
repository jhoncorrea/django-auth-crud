from django.db import models
# importo el modelo User para usarlo con la tabla Task
from django.contrib.auth.models import User

# Create your models here.


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

# esto sirve para verlo en el backend de manera personalizada


    def __str__(self):
        return self.title + ' - ' + self.user.username
