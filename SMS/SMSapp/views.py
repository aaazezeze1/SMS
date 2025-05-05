from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from .models import TodoItem

# Create your views here.
def home(request):
    return render(request, "home.html")

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # redirect to home page if login is successful
            auth_login(request, user)
            return redirect('home')  
        else:
            return render(request, 'login.html', {'error': 'Invalid Credentials. Please Try Again.'})
        
    return render(request, "login.html")

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # create the user
        User.objects.create_user(username=username, password=password)

        # authenticate and log in
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # if successful then redirect to home page
            auth_login(request, user)
            return redirect('home')
        else:
            # show the error message in the div
            return render(request, 'register.html', {'error': 'There was an issue logging you in after registration.'})

    return render(request, "register.html")

def todos(request):
    items = TodoItem.objects.all()
    return render(request, "todos.html", {"todos": items})