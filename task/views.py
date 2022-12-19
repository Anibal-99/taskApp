from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
# este login crea una cookie para que el navegador pueda saber que se esta autenticando el usuario
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# con el UserCreationForm lo que nos da es un formulario de django para crear interfaces de inicio de sesion, nos da ya un formulario creado


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    "error": 'User already exists'
                })

        return render(request, 'signup.html', {
            'form': UserCreationForm,
            "error": 'password do not match'
        })

@login_required
def tasks(request):
    # esto me devuelve todas las tareas que estan en la db
    tasks = Task.objects.filter(user=request.user, date_completed__isnull=True)
    # esta consulta de arriba lo que hace es traerme todas las tareas del usuario que se encuentra logueado
    # ademas tambien trae las tareas que no tengan una fecha de completado
    return render(request, 'tasks.html', {
        'tasks': tasks
    })
@login_required
def tasks_completed(request):
    # esto me devuelve todas las tareas que estan en la db
    tasks = Task.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    # esta consulta de arriba lo que hace es traerme todas las tareas del usuario que se encuentra logueado
    # ademas tambien trae las tareas que no tengan una fecha de completado
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'sigin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'sigin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tasks')

@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Please provide valida data'
            })

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error updating task'})

@login_required
def complete_task(request, task_id):
    task= get_object_or_404(Task, pk= task_id, user=request.user)
    if request.method=="POST":
        task.date_completed = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task= get_object_or_404(Task, pk= task_id, user=request.user)
    if request.method=="POST":
        task.delete()
        return redirect('tasks')
