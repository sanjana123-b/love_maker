from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .forms import RegisterForm, LoginForm, ProfileForm, UserUpdateForm
from .models import Profile


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to LoveMatch! Complete your profile to get started.')
            return redirect('profile_edit')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard_view(request):
    from matching.models import Match
    profile = request.user.profile
    total_profiles = Profile.objects.exclude(user=request.user).count()
    matches_count = Match.objects.filter(Q(user1=request.user) | Q(user2=request.user)).count()
    context = {
        'profile': profile,
        'total_profiles': total_profiles,
        'matches_count': matches_count,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_edit_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def profile_list_view(request):
    profiles = Profile.objects.exclude(user=request.user).select_related('user')

    # Search & Filter
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    min_age = request.GET.get('min_age', '')
    max_age = request.GET.get('max_age', '')
    interest = request.GET.get('interest', '')

    if query:
        profiles = profiles.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(bio__icontains=query)
        )
    if city:
        profiles = profiles.filter(city__icontains=city)
    if interest:
        profiles = profiles.filter(interests__icontains=interest)
    if min_age:
        try:
            from datetime import date, timedelta
            max_birth = date.today() - timedelta(days=int(min_age) * 365)
            profiles = profiles.filter(birth_date__lte=max_birth)
        except (ValueError, TypeError):
            pass
    if max_age:
        try:
            from datetime import date, timedelta
            min_birth = date.today() - timedelta(days=int(max_age) * 365)
            profiles = profiles.filter(birth_date__gte=min_birth)
        except (ValueError, TypeError):
            pass

    # Get unique cities for filter dropdown
    all_cities = Profile.objects.exclude(city='').values_list('city', flat=True).distinct()

    context = {
        'profiles': profiles,
        'query': query,
        'city': city,
        'min_age': min_age,
        'max_age': max_age,
        'interest': interest,
        'all_cities': all_cities,
    }
    return render(request, 'accounts/profile_list.html', context)


@login_required
def profile_detail_view(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    context = {
        'profile': profile,
    }
    return render(request, 'accounts/profile_detail.html', context)
