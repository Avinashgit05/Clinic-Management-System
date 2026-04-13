from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.forms import LoginForm, PatientRegistrationForm
from patients.models import PatientProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:redirect')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
        return redirect('accounts:redirect')
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:redirect')
    form = PatientRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        PatientProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, "Account created! Please complete your profile.")
        return redirect('patients:profile')
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')


@login_required
def redirect_view(request):
    user = request.user
    if user.is_superuser or user.is_admin_user:
        return redirect('admin_panel:dashboard')
    if user.is_doctor:
        return redirect('doctors:dashboard')
    if user.is_patient:
        return redirect('patients:dashboard')
    return redirect('accounts:login')
