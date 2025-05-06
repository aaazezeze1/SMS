from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import authenticate, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

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

def logout(request):
    auth_logout(request)
    messages.success(request, ("You have been logged out"))
    return redirect("login")

@login_required
def reset(request):
    user = request.user

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')

        if new_username:
            user.username = new_username

        if new_password:
            user.set_password(new_password)

        user.save()

        # Update session *after* saving password
        update_session_auth_hash(request, user)

        messages.success(request, "Credentials updated successfully.")
        return redirect('home')

    return render(request, 'reset.html')
