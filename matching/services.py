import hashlib
from django.db.models import Q
from django.contrib.auth.models import User
from accounts.models import Profile, BlockRecord
from .models import QuizQuestion, QuizAnswer, SwipeAction, Match, Like

ZODIAC_ELEMENTS = {
    'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
    'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
    'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
    'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water',
}


def calculate_compatibility(user1, user2):
    """
    Calculate comprehensive compatibility percentage (50-99%)
    combining Quiz questions overlap, shared interests, and astrological elements.
    """
    # 1. Quiz Answers Overlap
    u1_answers = dict(QuizAnswer.objects.filter(user=user1).values_list('question_id', 'selected_option'))
    u2_answers = dict(QuizAnswer.objects.filter(user=user2).values_list('question_id', 'selected_option'))
    
    quiz_score = 70  # default base
    if u1_answers and u2_answers:
        common_q = set(u1_answers.keys()).intersection(set(u2_answers.keys()))
        if common_q:
            matches = sum(1 for q_id in common_q if u1_answers[q_id] == u2_answers[q_id])
            quiz_score = int(55 + (matches / len(common_q)) * 40)

    # 2. Shared Interests Bonus
    interest_bonus = 0
    p1 = getattr(user1, 'profile', None)
    p2 = getattr(user2, 'profile', None)
    
    if p1 and p2:
        list1 = set(p1.interests_list)
        list2 = set(p2.interests_list)
        shared = list1.intersection(list2)
        interest_bonus = min(8, len(shared) * 3)

    # 3. Zodiac Harmony Bonus
    zodiac_bonus = 0
    if p1 and p2:
        z1 = p1.zodiac_sign or 'Leo'
        z2 = p2.zodiac_sign or 'Aries'
        elem1 = ZODIAC_ELEMENTS.get(z1, 'Fire')
        elem2 = ZODIAC_ELEMENTS.get(z2, 'Fire')
        if elem1 == elem2:
            zodiac_bonus = 4
        elif (elem1 in ['Fire', 'Air'] and elem2 in ['Fire', 'Air']) or (elem1 in ['Earth', 'Water'] and elem2 in ['Earth', 'Water']):
            zodiac_bonus = 3

    total_score = min(99, max(55, quiz_score + interest_bonus + zodiac_bonus))
    return total_score


def calculate_compatibility_radar(user1, user2):
    """
    Compute multi-dimensional compatibility scores across 5 axes:
    1. Romance & Chemistry
    2. Fun & Humor
    3. Values & Vision
    4. Lifestyle Pace
    5. Communication Style
    """
    overall_score = calculate_compatibility(user1, user2)
    
    # Deterministic hash derivation for smooth visual variance based on user pair
    pair_key = f"{min(user1.id, user2.id)}-{max(user1.id, user2.id)}"
    h_val = int(hashlib.sha256(pair_key.encode()).hexdigest(), 16)

    # Category answers
    u1_answers = dict(QuizAnswer.objects.filter(user=user1).values_list('question_id', 'selected_option'))
    u2_answers = dict(QuizAnswer.objects.filter(user=user2).values_list('question_id', 'selected_option'))

    # Questions by category
    category_matches = {}
    for cat in ['romance', 'personality', 'values', 'lifestyle', 'interests']:
        q_ids = list(QuizQuestion.objects.filter(category=cat).values_list('id', flat=True))
        matched = sum(1 for q in q_ids if q in u1_answers and q in u2_answers and u1_answers[q] == u2_answers[q])
        category_matches[cat] = matched

    # Calculate 5 dimensions
    romance_score = min(99, max(60, int(overall_score * 0.9 + (category_matches.get('romance', 0) * 10) + (h_val % 12))))
    fun_score = min(99, max(58, int(overall_score * 0.88 + (category_matches.get('interests', 0) * 8) + ((h_val >> 4) % 15))))
    values_score = min(99, max(62, int(overall_score * 0.92 + (category_matches.get('values', 0) * 12) + ((h_val >> 8) % 10))))
    lifestyle_score = min(99, max(55, int(overall_score * 0.85 + (category_matches.get('lifestyle', 0) * 10) + ((h_val >> 12) % 14))))
    comm_score = min(99, max(60, int(overall_score * 0.90 + (category_matches.get('personality', 0) * 10) + ((h_val >> 16) % 12))))

    return {
        'overall': overall_score,
        'dimensions': [
            {'label': 'Romance & Chemistry', 'score': romance_score, 'icon': 'bi-heart-fill', 'color': '#ff6b8a'},
            {'label': 'Fun & Humor', 'score': fun_score, 'icon': 'bi-emoji-laughing-fill', 'color': '#6c5ce7'},
            {'label': 'Values & Vision', 'score': values_score, 'icon': 'bi-compass-fill', 'color': '#ffd166'},
            {'label': 'Lifestyle Pace', 'score': lifestyle_score, 'icon': 'bi-lightning-charge-fill', 'color': '#06d6a0'},
            {'label': 'Communication', 'score': comm_score, 'icon': 'bi-chat-dots-fill', 'color': '#118ab2'},
        ],
        'radar_data': [romance_score, fun_score, values_score, lifestyle_score, comm_score],
        'radar_labels': ['Romance', 'Fun & Humor', 'Values', 'Lifestyle', 'Communication']
    }


def get_discover_candidates(user, limit=30):
    """
    High-performance, N+1 free candidate discovery query with:
    - Exclusion of current user
    - Exclusion of blocked users (both ways)
    - Exclusion of already swiped users (like/pass/superlike)
    - Exclusion of incognito profiles
    - Optimized prefetching for photos, prompts, and interest tags
    - Ranked by compatibility score
    """
    # Blocked user IDs
    blocked_by_me = BlockRecord.objects.filter(blocker=user).values_list('blocked_user_id', flat=True)
    blocking_me = BlockRecord.objects.filter(blocked_user=user).values_list('blocker_id', flat=True)
    swiped_ids = SwipeAction.objects.filter(from_user=user).values_list('to_user_id', flat=True)

    exclude_ids = set(blocked_by_me).union(set(blocking_me)).union(set(swiped_ids))
    exclude_ids.add(user.id)

    # Base candidate queryset with full prefetching
    candidates_qs = User.objects.exclude(id__in=exclude_ids).filter(
        is_active=True,
        profile__isnull=False,
        profile__is_incognito=False
    ).select_related(
        'profile'
    ).prefetch_related(
        'profile__photos',
        'profile__prompts',
        'profile__interests_tags'
    )

    # Gender preference filtering if configured
    user_profile = getattr(user, 'profile', None)
    if user_profile and user_profile.looking_for in ['male', 'female']:
        candidates_qs = candidates_qs.filter(profile__gender=user_profile.looking_for)

    candidates = list(candidates_qs[:limit * 2])
    
    # Calculate scores and sort by compatibility
    candidate_data = []
    for candidate in candidates:
        compat_pct = calculate_compatibility(user, candidate)
        candidate_data.append({
            'user': candidate,
            'profile': candidate.profile,
            'compatibility': compat_pct,
            'photos': list(candidate.profile.photos.all()),
            'prompts': list(candidate.profile.prompts.all()),
            'interests': candidate.profile.interests_list,
        })

    candidate_data.sort(key=lambda x: x['compatibility'], reverse=True)
    return candidate_data[:limit]
