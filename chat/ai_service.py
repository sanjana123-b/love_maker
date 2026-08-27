import os
import random
from django.conf import settings
from matching.models import QuizAnswer, QuizQuestion


def generate_spark_icebreakers(match, current_user):
    """
    Generate 3 tailored, engaging, contextual conversation starters for a match
    using Google Gemini API (gemini-3.6-flash) or intelligent heuristic fallback based on shared hobbies and quiz answers.
    """
    other_user = match.get_other_user(current_user)
    u1_profile = getattr(current_user, 'profile', None)
    u2_profile = getattr(other_user, 'profile', None)

    u1_name = current_user.first_name or current_user.username
    u2_name = other_user.first_name or other_user.username

    u1_interests = u1_profile.interests_list if u1_profile else []
    u2_interests = u2_profile.interests_list if u2_profile else []
    shared_interests = list(set(u1_interests).intersection(set(u2_interests)))

    z1 = getattr(u1_profile, 'zodiac_sign', 'Aries')
    z2 = getattr(u2_profile, 'zodiac_sign', 'Leo')

    # Check for Google Gemini API key
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
    
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            prompt = (
                f"You are a charming, witty dating coach and icebreaker assistant for the dating app LoveMatch.\n"
                f"Sender: {u1_name}, Zodiac: {z1}, Interests: {', '.join(u1_interests) if u1_interests else 'various'}.\n"
                f"Recipient: {u2_name}, Zodiac: {z2}, Interests: {', '.join(u2_interests) if u2_interests else 'various'}.\n"
                f"Shared Interests: {', '.join(shared_interests) if shared_interests else 'none specifically listed'}.\n"
                f"Task: Generate exactly 3 fun, playful, non-cheesy, unique icebreaker questions for {u1_name} to send to {u2_name}.\n"
                f"Strict Format Requirement: Return ONLY 3 numbered lines (1., 2., 3.) with the exact message to send. No preamble, no bold titles, no explanations. Max 25 words per question."
            )
            
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
            )
            
            lines = [l.strip() for l in response.text.strip().split('\n') if l.strip()]
            cleaned_icebreakers = []
            for line in lines:
                cleaned = line.lstrip('0123456789.-)>*#" ').rstrip('"* ')
                if cleaned and len(cleaned) > 8:
                    cleaned_icebreakers.append(cleaned)
            
            if len(cleaned_icebreakers) >= 3:
                return cleaned_icebreakers[:3]
            elif cleaned_icebreakers:
                while len(cleaned_icebreakers) < 3:
                    cleaned_icebreakers.append(f"Hey {u2_name}! What's the most exciting thing that happened to you this week?")
                return cleaned_icebreakers[:3]
        except Exception as e:
            # Fall back gracefully to heuristic engine
            pass

    # High quality dynamic algorithmic icebreaker generator
    icebreakers = []

    # 1. Based on shared interests or individual interests
    if shared_interests:
        top_interest = shared_interests[0]
        icebreakers.append(f"I saw we both enjoy {top_interest}! What's your absolute favorite experience with that?")
    elif u2_interests:
        pick = random.choice(u2_interests)
        icebreakers.append(f"Your passion for {pick} caught my eye! What got you started on that?")
    else:
        icebreakers.append(f"Hey {u2_name}! What's the most exciting thing that happened to you this week?")

    # 2. Zodiac / playful banter
    if z1 and z2:
        icebreakers.append(f"As a {z1} matching with a {z2}, are we destined for chaotic adventures or deep late-night talks?")
    else:
        icebreakers.append("Truth or Dare, or tell me your most controversial food opinion?")

    # 3. Fun hypothetical / date dilemma
    hypotheticals = [
        "If we had 24 hours in a city with an unlimited budget, where are we heading first?",
        "Quick: coffee date with good music, or an impromptu road trip to find the best street food?",
        "What's one song that instantly puts you in a good mood no matter what?",
        "What's your go-to weekend comfort food when you want to treat yourself?",
    ]
    icebreakers.append(random.choice(hypotheticals))

    return icebreakers[:3]
