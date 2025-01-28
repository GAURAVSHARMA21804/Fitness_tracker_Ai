# users_auth app  views here.
from django.shortcuts import render,HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomSignupForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import CustomUser
from django.contrib.auth import authenticate, login as auth_login




def user_home(request):
    return HttpResponse("hello user auth home")
#signup page view
def signup(request):
    return render(request, 'users_auth/signup.html')
#login page view
def login(request):
    return render(request, 'users_auth/login.html')


# signup view logic
def signup_view(request):
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save()  
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('users_auth:login')  
        else:
            messages.error(request, "There was an error creating your account. Please correct the errors below.")
    else:
        form = CustomSignupForm()
    
    return render(request, 'users_auth/signup.html', {'form': form})

#login view logic
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Attempting to authenticate user: {username}")  

        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(f"User authenticated: {user.username}")  
            auth_login(request, user)

            # Redirecting based on the user's admin status
            if user.is_admin:
                request.session['is_admin'] = True  # Set role in session
                print("Redirecting to admin dashboard")  
                return redirect('tracker:admin_panel_dashboard')
            else:
                request.session['is_admin'] = False
                print("Redirecting to user dashboard")  
                return redirect('tracker:users_dashboard')

        else:
            print("Authentication failed!")  
            messages.error(request, 'Invalid username or password')  
            return render(request, 'users_auth/login.html')

    # GET request, show the login form
    return render(request, 'users_auth/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('tracker:home')