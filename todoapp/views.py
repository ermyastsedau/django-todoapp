from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import todo
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def home(request):
    if request.method == 'POST':
        task = request.POST.get('task')
        new_todo = todo(user = request.user, todo_name = task)
        new_todo.save()

    # GET parameters for filtering
    selected_date = request.GET.get('date')
    selected_status = request.GET.get('status')

    # Base query (filter by user)
    todos_query = todo.objects.filter(user=request.user)

    # Filter by date if provided
    if selected_date:
        todos_query = todos_query.filter(created_at__date=selected_date)

    # Filter by status if provided
    if selected_status == "True":
        todos_query = todos_query.filter(status=True)
    elif selected_status == "False":
        todos_query = todos_query.filter(status=False)

    context = {
        'todos': todos_query,
        'selected_date': selected_date,
        'selected_status': selected_status,
    }
    return render(request, 'todoapp/todo.html', context)

def editTask(request, pk):
    task = get_object_or_404(todo, pk=pk, user=request.user)

    if request.method == 'POST':
        updated_name = request.POST.get('task')
        if updated_name:
            task.todo_name = updated_name
            task.save()
            return redirect('home-page')

    context = {
        'task': task
    }
    return render(request, 'todoapp/edit.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if len(password) < 3:
            messages.error(request, 'Password must be atleast 3 character')
            return redirect('register')
        get_all_user_by_username = User.objects.filter(username=username)
        if get_all_user_by_username:
            messages.error(request, 'Username already exist')

        new_user = User.objects.create_user(username=username, email=email, password=password)
        new_user.save()

        messages.success(request, 'User successfully created, login now')
        return redirect('login')

    return render(request, 'todoapp/register.html', {})

def logoutview(request):
    logout(request)
    return redirect('login')

def loginpage(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('pass')

        validate_user = authenticate(username=username, password=password)
        if validate_user is not None:
            login(request, validate_user)
            return redirect('home-page')
        else:
            messages.error(request, 'Error, Wrong user detail')
            return redirect('login')
    return render(request, 'todoapp/login.html', {})

@login_required
def deleteTask(request, name):
    get_todo = todo.objects.get(user = request.user, todo_name = name)
    get_todo.delete()
    return redirect('home-page')

@login_required
def updateTask(request, name):
    get_todo = todo.objects.get(user = request.user, todo_name = name)
    get_todo.status = True
    get_todo.save()

    return redirect('home-page')