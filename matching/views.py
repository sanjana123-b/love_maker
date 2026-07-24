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


import hashlib

ZODIAC_ELEMENTS = {
    'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
    'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
    'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
    'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water',
}

ZODIAC_CHOICES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

@login_required
def love_match_view(request):
    """Love Match calculator view with instant name/zodiac matching and profile matching."""
    other_users = User.objects.exclude(pk=request.user.pk).select_related('profile')
    
    match_result = None
    mode = request.GET.get('mode', 'names')
    target_user_id = request.GET.get('target_user_id')

    if target_user_id:
        mode = 'profile'

    if request.method == 'POST' or target_user_id:
        post_mode = request.POST.get('mode')
        if post_mode == 'profile' or mode == 'profile' or target_user_id:
            user_id = request.POST.get('target_user') or target_user_id
            if user_id:
                target_user = get_object_or_404(User, pk=user_id)
                score = calculate_compatibility(request.user, target_user)
                
                combined_seed = f"{min(request.user.id, target_user.id)}-{max(request.user.id, target_user.id)}"
                h_val = int(hashlib.md5(combined_seed.encode()).hexdigest(), 16)
                
                romance_score = 65 + (h_val % 31)
                fun_score = 70 + ((h_val >> 3) % 28)
                comm_score = 60 + ((h_val >> 6) % 36)
                trust_score = 72 + ((h_val >> 9) % 25)

                name1 = request.user.first_name or request.user.username
                name2 = target_user.first_name or target_user.username
                zodiac1 = getattr(request.user.profile, 'zodiac_sign', 'Aries') if hasattr(request.user, 'profile') else 'Aries'
                zodiac2 = getattr(target_user.profile, 'zodiac_sign', 'Leo') if hasattr(target_user, 'profile') else 'Leo'

                match_result = generate_love_verdict(
                    name1=name1,
                    name2=name2,
                    score=score,
                    romance_score=romance_score,
                    fun_score=fun_score,
                    comm_score=comm_score,
                    trust_score=trust_score,
                    zodiac1=zodiac1,
                    zodiac2=zodiac2,
                    target_user=target_user
                )

        else:
            name1 = request.POST.get('name1', '').strip()
            name2 = request.POST.get('name2', '').strip()
            zodiac1 = request.POST.get('zodiac1', 'Aries')
            zodiac2 = request.POST.get('zodiac2', 'Leo')

            if name1 and name2:
                seed = f"{name1.lower()}-{name2.lower()}"
                h_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)
                
                score = 65 + (h_val % 34)
                
                elem1 = ZODIAC_ELEMENTS.get(zodiac1, 'Fire')
                elem2 = ZODIAC_ELEMENTS.get(zodiac2, 'Fire')
                if elem1 == elem2 or (elem1 in ['Fire', 'Air'] and elem2 in ['Fire', 'Air']) or (elem1 in ['Earth', 'Water'] and elem2 in ['Earth', 'Water']):
                    score = min(99, score + 4)

                romance_score = min(99, 60 + (h_val % 38))
                fun_score = min(99, 65 + ((h_val >> 4) % 33))
                comm_score = min(99, 58 + ((h_val >> 8) % 39))
                trust_score = min(99, 70 + ((h_val >> 12) % 28))

                match_result = generate_love_verdict(
                    name1=name1,
                    name2=name2,
                    score=score,
                    romance_score=romance_score,
                    fun_score=fun_score,
                    comm_score=comm_score,
                    trust_score=trust_score,
                    zodiac1=zodiac1,
                    zodiac2=zodiac2
                )

    context = {
        'other_users': other_users,
        'zodiac_choices': ZODIAC_CHOICES,
        'match_result': match_result,
        'mode': mode,
    }
    return render(request, 'matching/love_match.html', context)


def generate_love_verdict(name1, name2, score, romance_score, fun_score, comm_score, trust_score, zodiac1='Aries', zodiac2='Leo', target_user=None):
    """Generate structured funny & romantic love match breakdown report."""
    if score >= 90:
        badge = "Match Made in Heaven 💖"
        badge_color = "success"
        verdict_title = f"{name1} & {name2} are Absolute Soulmates!"
        quote = "The stars literally aligned for you two. Expect long talks, midnight snacks, and undeniable chemistry!"
    elif score >= 80:
        badge = "High Chemistry 🔥"
        badge_color = "danger"
        verdict_title = f"{name1} & {name2} Have Explosive Spark!"
        quote = "Electric energy! You two balance each other perfectly — like coffee and late mornings."
    elif score >= 70:
        badge = "Harmonious Connection ✨"
        badge_color = "info"
        verdict_title = f"{name1} & {name2} Share Great Harmony!"
        quote = "A solid, comforting bond with endless potential. Keep the laughs coming and the connection will thrive!"
    else:
        badge = "Playful Wildcard 😜"
        badge_color = "warning"
        verdict_title = f"{name1} & {name2} Have Unpredictable Charm!"
        quote = "Opposites attract! Things will never be boring between you two. Expect fun surprises around every corner."

    elem1 = ZODIAC_ELEMENTS.get(zodiac1, 'Fire')
    elem2 = ZODIAC_ELEMENTS.get(zodiac2, 'Fire')
    if elem1 == elem2:
        zodiac_note = f"Both {zodiac1} and {zodiac2} belong to the {elem1} element — intense mutual understanding!"
    elif (elem1 in ['Fire', 'Air'] and elem2 in ['Fire', 'Air']):
        zodiac_note = f"{zodiac1} ({elem1}) fuels {zodiac2} ({elem2}) — inspiring and energetic vibe!"
    elif (elem1 in ['Earth', 'Water'] and elem2 in ['Earth', 'Water']):
        zodiac_note = f"{zodiac1} ({elem1}) & {zodiac2} ({elem2}) nurture each other — deep emotional stability!"
    else:
        zodiac_note = f"{zodiac1} ({elem1}) & {zodiac2} ({elem2}) bring dynamic contrast — exciting friction!"

    return {
        'name1': name1,
        'name2': name2,
        'score': score,
        'romance_score': romance_score,
        'fun_score': fun_score,
        'comm_score': comm_score,
        'trust_score': trust_score,
        'badge': badge,
        'badge_color': badge_color,
        'verdict_title': verdict_title,
        'quote': quote,
        'zodiac1': zodiac1,
        'zodiac2': zodiac2,
        'zodiac_note': zodiac_note,
        'target_user': target_user,
    }

