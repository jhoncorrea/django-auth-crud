from django.contrib import admin
#importo el modelo creado
from .models import Task

#con esto puedo ver otros campos en el admin
class TaskAdmin(admin.ModelAdmin):
    #es una tupla por lo tanto debe tener una coma luego del campo
    readonly_fields = ("created" , )

# Register your models here.
admin.site.register(Task, TaskAdmin)