from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
# clase para la creación y autenticación de usuarios
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# voy a importar el modelo de usuario
from django.contrib.auth.models import User
#para que cree la cookie
from django.contrib.auth import login, logout, authenticate
#importo mi modelo
from .models import Task
#importo el form de mi modelo
from .forms import TaskForm
from django.utils import timezone
#importamos un decorador para que proteja las rutas
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            # le voy a pasar el formulario
            'form': UserCreationForm
        })
    else:
        # verifico que las contraseñas sean iguales
        if request.POST['password1'] == request.POST['password2']:
            try:
                # creo el usuario y lo asigno a user
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )
                # guardo el usuario
                user.save()           
                #llamo a la funcion login que crea la cookie
                login(request, user)     
                return redirect('tasks')            
            except:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'ya existe el usuario'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'las contraseñas no coinciden'
        })


@login_required
def tasks(request):
    #muestra las tareas que NO están completadas y que le pertenecen al usuario de la sesión actual
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    #muestra todas las tareas sin filtro
    #tasks = Task.objects.all()
    return render(request, 'tasks.html', {"tasks": tasks})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {"tasks": tasks})

@login_required
#el task_id es el parámetro que se recibe como id de la tarea
def task_detail(request, task_id):
    if request.method == 'GET':
    #es task almaceno la variable que acabo de encontrar cuyo pk es el task_id que recibi
    #pero mejor a eso es el get_object_or_404...para manejar los errores
    #task = Task.objects.get(pk=task_id)
        #también el otro filtro es que solo edite las tareas del propio usuario
        task = get_object_or_404(Task, pk=task_id, user=request.user)
    #de esta forma se llena la tarea en el formulario
        form = TaskForm(instance=task) #le paso el objeto que crea una instancia de la tarea y lo muestra en el formulario
    #esa tarea que es un objeto se la mando entre llaves como diccionario
    #la claves es 'task': y el valor es el objeto
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            #obtengo los datos de la tarea cuyo id recibo y los guardo en task
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            #en un nuevo form guardo los nuevos datos de la tarea
            form = TaskForm(request.POST, instance=task)
            #guardo el form en la BD
            form.save()
            #redirijo
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Error al actualizar la tarea'
                })
        
@login_required        
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')    
    
@login_required    
def delete_task(request, task_id):
    #obtengo la tarea que le pertecene al usuario cuyo id es el seleccionado
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')    

@login_required
def create_task(request):
    if request.method == "GET":
        return render(request, 'create_task.html', {"form": TaskForm})
    else:
        try:
            #en la variable form guardo los datos capturados del formulario
            form = TaskForm(request.POST)
            #new_task CONTIENE la nueva tarea, commit=False es para que no lo guarde en la BD
            new_task = form.save(commit=False)
            # cada tarea tiene un usuario por eso debemos agregar a la tarea su usuario
            #request.user nos da el usuario
            new_task.user = request.user
            #aqui se guarda en la BD
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {"form": TaskForm, "error": "Error creating task."})

@login_required
def signout(request):
    #le paso la función logout
    logout(request)
    return redirect('home')


def signin(request):
    #si el método es GET devuelve el formulario
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    #entonces debe ser POST y eso significa que está enviando datos
    else:
        #en el objeto user almaceno la autenticación
        #le mando el username y password y compruebo si existe, en caso de ser verdad lo asigno a user
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        #si el objeto está vacío es porque no hay usuario, es decir la autenticación falló ya sea en la clave o usuario
        if user is None:
            #lo mantengo en el signin.html y le digo su error
            return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})
        #si hay user entonces en la función login almaceno su cookie
        login(request, user)
        #redirecciona tasks
        return redirect('tasks')