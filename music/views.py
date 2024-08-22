from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User, auth 
# Create your views here.

def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_login = auth.authenticate(username = username, password = password)
        auth.login(request,user_login)
        return redirect('/')
    #return render(request, 'login.html')

def logout(request):
    pass

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists:
                messages.info(request, 'Email or Username already exists!')
                return redirect('signup')
            else:
                user = User.objects.create(username=username, email=email, password=password) 
                user.save()
                user_login = auth.authenticate(username = username, password = password)
                auth.login(request,user_login)
                return redirect('/')
        else:
            messages.info(request,'Password not match!')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

