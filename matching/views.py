from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import QuizQuestion, QuizAnswer, Like, Match

DEFAULT_QUESTIONS = [
    {
        'text': 'What is your ideal weekend activity?',
        'category': 'lifestyle',
        'option_a': 'Outdoor adventure & hiking',
        'option_b': 'Cozy night with a movie or book',
        'option_c': 'Fine dining & party with friends',
        'option_d': 'Creative hobbies & gaming',
    },
    {
        'text': 'How do you express affection in a relationship?',
        'category': 'romance',
        'option_a': 'Words of affirmation & sweet texts',
        'option_b': 'Quality time together without distractions',
        'option_c': 'Thoughtful gifts & surprises',
        'option_d': 'Physical touch & closeness',
    },
    {
        'text': 'What is your long-term goal in love?',
        'category': 'values',
        'option_a': 'Finding a lifelong soulmate',
        'option_b': 'Having fun & seeing where it goes',
        'option_c': 'Building a family & home',
        'option_d': 'Travelling the world with a partner',
    },
    {
        'text': 'How do you handle disagreements in a relationship?',
        'category': 'personality',
        'option_a': 'Talk it out calmly right away',
        'option_b': 'Take space to cool down, then discuss',
        'option_c': 'Use humor & warmth to diffuse tension',
        'option_d': 'Compromise quickly to maintain peace',
    },
    {
        'text': 'What role does travel play in your life?',
        'category': 'interests',
        'option_a': 'Essential — I explore new places whenever I can',
        'option_b': 'Enjoy occasional relaxing getaways',
        'option_c': 'Prefer staycations & local hidden spots',
        'option_d': 'Travel mainly for special events & occasions',
    },
]

def seed_quiz_questions_if_empty():
    if QuizQuestion.objects.count() == 0:
        for q_data in DEFAULT_QUESTIONS:
            QuizQuestion.objects.create(**q_data)

def calculate_compatibility(user1, user2):
    """Calculate compatibility percentage based on matching quiz answers."""
    u1_answers = dict(QuizAnswer.objects.filter(user=user1).values_list('question_id', 'selected_option'))
    u2_answers = dict(QuizAnswer.objects.filter(user=user2).values_list('question_id', 'selected_option'))
    
    if not u1_answers or not u2_answers:
        return 75  # Default base compatibility
    
    common_questions = set(u1_answers.keys()).intersection(set(u2_answers.keys()))
    if not common_questions:
        return 75
    
    matches = sum(1 for q_id in common_questions if u1_answers[q_id] == u2_answers[q_id])
    score = int(60 + (matches / len(common_questions)) * 40)
    return min(99, max(60, score))

@login_required
def quiz_view(request):
    seed_quiz_questions_if_empty()
    questions = QuizQuestion.objects.all()
    
    if request.method == 'POST':
        for question in questions:
            field_name = f'question_{question.id}'
            selected_option = request.POST.get(field_name)
            if selected_option in ['A', 'B', 'C', 'D']:
                QuizAnswer.objects.update_or_create(
                    user=request.user,
                    question=question,
                    defaults={'selected_option': selected_option}
                )
        messages.success(request, 'Your quiz answers have been saved! Your compatibility matching is now updated.')
        return redirect('quiz')

    user_answers = {
        ans.question_id: ans.selected_option
        for ans in QuizAnswer.objects.filter(user=request.user)
    }
    
    total_q = questions.count()
    answered_q = len(user_answers)
    progress_pct = int((answered_q / total_q) * 100) if total_q > 0 else 0
    
    context = {
        'questions': questions,
        'user_answers': user_answers,
        'total_q': total_q,
        'answered_q': answered_q,
        'progress_pct': progress_pct,
    }
    return render(request, 'matching/quiz.html', context)

@login_required
def like_user_view(request, user_id):
    to_user = get_object_or_404(User, pk=user_id)
    if to_user == request.user:
        messages.warning(request, "You cannot like yourself!")
        return redirect('profile_detail', pk=user_id)

    like, created = Like.objects.get_or_create(from_user=request.user, to_user=to_user)
    
    if not created:
        like.delete()
        messages.info(request, f"Unliked {to_user.first_name or to_user.username}.")
    else:
        # Check for mutual like
        mutual_like = Like.objects.filter(from_user=to_user, to_user=request.user).exists()
        if mutual_like:
            # Order user IDs consistently
            u1, u2 = (request.user, to_user) if request.user.id < to_user.id else (to_user, request.user)
            match, _ = Match.objects.get_or_create(user1=u1, user2=u2)
            messages.success(request, f"🎉 It's a Match! You and {to_user.first_name or to_user.username} liked each other!")
            return redirect('matches')
        else:
            messages.success(request, f"Liked {to_user.first_name or to_user.username}!")
            
    return redirect('profile_detail', pk=user_id)

@login_required
def matches_list_view(request):
    # Get mutual matches
    matches_qs = Match.objects.filter(Q(user1=request.user) | Q(user2=request.user)).select_related('user1__profile', 'user2__profile')
    
    matches_data = []
    for match in matches_qs:
        other_user = match.get_other_user(request.user)
        compat_pct = calculate_compatibility(request.user, other_user)
        matches_data.append({
            'match': match,
            'user': other_user,
            'profile': getattr(other_user, 'profile', None),
            'compatibility': compat_pct,
        })

    # Liked users
    likes_given = Like.objects.filter(from_user=request.user).select_related('to_user__profile')
    liked_users = [like.to_user for like in likes_given]

    # Users who liked me
    likes_received = Like.objects.filter(to_user=request.user).select_related('from_user__profile')
    admirers = [like.from_user for like in likes_received if not Like.objects.filter(from_user=request.user, to_user=like.from_user).exists()]

    context = {
        'matches_data': matches_data,
        'liked_users': liked_users,
        'admirers': admirers,
    }
    return render(request, 'matching/matches.html', context)
