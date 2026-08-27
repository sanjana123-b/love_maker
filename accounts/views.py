from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import date

from .forms import RegisterForm, LoginForm, ProfileForm, UserUpdateForm
from .models import Profile, ProfilePhoto, ProfilePrompt, InterestTag, BlockRecord, UserReport
from matching.models import Match, Like
from matching.services import calculate_compatibility, calculate_compatibility_radar


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
            messages.success(request, 'Welcome to LoveMatch! Complete your profile to find your best matches.')
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
    profile = request.user.profile
    
    # Exclude blocked users from counts
    blocked_by_me = BlockRecord.objects.filter(blocker=request.user).values_list('blocked_user_id', flat=True)
    blocking_me = BlockRecord.objects.filter(blocked_user=request.user).values_list('blocker_id', flat=True)
    blocked_ids = set(blocked_by_me).union(set(blocking_me))

    total_profiles = Profile.objects.exclude(user=request.user).exclude(user_id__in=blocked_ids).filter(is_incognito=False).count()
    matches_count = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user),
        is_active=True
    ).exclude(Q(user1_id__in=blocked_ids) | Q(user2_id__in=blocked_ids)).count()

    admirers_count = Like.objects.filter(to_user=request.user).exclude(from_user=request.user).exclude(from_user_id__in=blocked_ids).count()

    context = {
        'profile': profile,
        'total_profiles': total_profiles,
        'matches_count': matches_count,
        'admirers_count': admirers_count,
        'profile_strength': profile.profile_strength,
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
            messages.success(request, 'Your profile has been successfully updated!')
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
    
    gallery_photos = profile.photos.all()
    prompt_answers = profile.prompts.all()
    all_interest_tags = InterestTag.objects.all()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'gallery_photos': gallery_photos,
        'prompt_answers': prompt_answers,
        'prompt_choices': ProfilePrompt.PROMPT_CHOICES,
        'all_interest_tags': all_interest_tags,
        'profile_strength': profile.profile_strength,
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
@require_POST
def upload_photo_view(request):
    """AJAX endpoint for uploading multi-photo gallery image."""
    profile = request.user.profile
    if profile.photos.count() >= 6:
        return JsonResponse({'status': 'error', 'message': 'Maximum 6 gallery photos allowed.'}, status=400)

    photo_file = request.FILES.get('photo')
    caption = request.POST.get('caption', '').strip()

    if photo_file:
        if photo_file.size > 5 * 1024 * 1024:
            return JsonResponse({'status': 'error', 'message': 'Photo size cannot exceed 5MB.'}, status=400)

        photo = ProfilePhoto.objects.create(
            profile=profile,
            image=photo_file,
            caption=caption,
            order=profile.photos.count()
        )
        return JsonResponse({
            'status': 'success',
            'photo_id': photo.id,
            'url': photo.image.url,
            'caption': photo.caption
        })
    return JsonResponse({'status': 'error', 'message': 'No photo provided.'}, status=400)


@login_required
@require_POST
def delete_photo_view(request, photo_id):
    """Deletes a gallery photo."""
    photo = get_object_or_404(ProfilePhoto, pk=photo_id, profile=request.user.profile)
    photo.delete()
    messages.info(request, "Photo removed from gallery.")
    return redirect('profile_edit')


@login_required
@require_POST
def save_prompt_view(request):
    """Creates or updates a profile prompt response."""
    question = request.POST.get('question', '').strip()
    answer = request.POST.get('answer', '').strip()

    if question and answer:
        ProfilePrompt.objects.update_or_create(
            profile=request.user.profile,
            question=question,
            defaults={'answer': answer}
        )
        messages.success(request, "Profile prompt saved!")
    return redirect('profile_edit')


@login_required
@require_POST
def delete_prompt_view(request, prompt_id):
    """Deletes a profile prompt answer."""
    prompt = get_object_or_404(ProfilePrompt, pk=prompt_id, profile=request.user.profile)
    prompt.delete()
    messages.info(request, "Prompt removed.")
    return redirect('profile_edit')


@login_required
def profile_list_view(request):
    # Exclude current user, blocked users, and incognito accounts
    blocked_by_me = BlockRecord.objects.filter(blocker=request.user).values_list('blocked_user_id', flat=True)
    blocking_me = BlockRecord.objects.filter(blocked_user=request.user).values_list('blocker_id', flat=True)
    blocked_ids = set(blocked_by_me).union(set(blocking_me))

    profiles = Profile.objects.exclude(user=request.user).exclude(user_id__in=blocked_ids).filter(
        is_incognito=False
    ).select_related('user').prefetch_related('photos', 'prompts')

    # Search & Filter
    query = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    min_age = request.GET.get('min_age', '')
    max_age = request.GET.get('max_age', '')
    interest = request.GET.get('interest', '').strip()

    if query:
        profiles = profiles.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(bio__icontains=query) |
            Q(occupation__icontains=query)
        )
    if city:
        profiles = profiles.filter(city__icontains=city)
    if interest:
        profiles = profiles.filter(
            Q(interests__icontains=interest) |
            Q(interests_tags__name__icontains=interest)
        ).distinct()
    
    today = date.today()
    if min_age:
        try:
            min_val = int(min_age)
            max_birth = date(today.year - min_val, today.month, today.day)
            profiles = profiles.filter(birth_date__lte=max_birth)
        except (ValueError, TypeError):
            pass
    if max_age:
        try:
            max_val = int(max_age)
            min_birth = date(today.year - max_val - 1, today.month, today.day)
            profiles = profiles.filter(birth_date__gte=min_birth)
        except (ValueError, TypeError):
            pass

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
    profile = get_object_or_404(
        Profile.objects.select_related('user').prefetch_related('photos', 'prompts', 'interests_tags'),
        pk=pk
    )

    # Check if blocked
    is_blocked = BlockRecord.objects.filter(
        Q(blocker=request.user, blocked_user=profile.user) | Q(blocker=profile.user, blocked_user=request.user)
    ).exists()
    if is_blocked:
        messages.error(request, "This profile is unavailable.")
        return redirect('profile_list')

    # Compute compatibility and radar breakdown
    compatibility = calculate_compatibility(request.user, profile.user) if profile.user != request.user else 100
    radar_data = calculate_compatibility_radar(request.user, profile.user) if profile.user != request.user else None

    # Check if already liked or matched
    has_liked = Like.objects.filter(from_user=request.user, to_user=profile.user).exists()
    is_match = Match.objects.filter(
        Q(user1=request.user, user2=profile.user) | Q(user1=profile.user, user2=request.user),
        is_active=True
    ).first()

    context = {
        'profile': profile,
        'compatibility': compatibility,
        'radar_data': radar_data,
        'has_liked': has_liked,
        'match': is_match,
        'gallery_photos': profile.photos.all(),
        'prompts': profile.prompts.all(),
    }
    return render(request, 'accounts/profile_detail.html', context)


# ════════ TRUST & SAFETY: BLOCK & REPORT ════════

@login_required
@require_POST
def block_user_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        messages.warning(request, "You cannot block yourself.")
        return redirect('dashboard')

    reason = request.POST.get('reason', '').strip()
    BlockRecord.objects.get_or_create(
        blocker=request.user,
        blocked_user=target_user,
        defaults={'reason': reason}
    )

    # Deactivate any active match between these users
    Match.objects.filter(
        Q(user1=request.user, user2=target_user) | Q(user1=target_user, user2=request.user)
    ).update(is_active=False)

    messages.success(request, f"You have blocked {target_user.first_name or target_user.username}.")
    return redirect('profile_list')


@login_required
@require_POST
def unblock_user_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    BlockRecord.objects.filter(blocker=request.user, blocked_user=target_user).delete()
    messages.success(request, f"Unblocked {target_user.first_name or target_user.username}.")
    return redirect('blocked_list')


@login_required
def blocked_list_view(request):
    blocked_records = BlockRecord.objects.filter(blocker=request.user).select_related('blocked_user__profile')
    return render(request, 'accounts/blocked_list.html', {'blocked_records': blocked_records})


@login_required
@require_POST
def report_user_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        messages.warning(request, "You cannot report yourself.")
        return redirect('dashboard')

    category = request.POST.get('category', 'harassment')
    description = request.POST.get('description', '').strip()

    if description:
        UserReport.objects.create(
            reporter=request.user,
            reported_user=target_user,
            category=category,
            description=description
        )
        messages.success(request, "Thank you. Your report has been submitted to Trust & Safety for immediate review.")
    return redirect('profile_list')
