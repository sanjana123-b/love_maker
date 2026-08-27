from django.core.management.base import BaseCommand
from accounts.models import InterestTag
from matching.models import QuizQuestion

DEFAULT_INTERESTS = [
    # Lifestyle & Outdoors
    {'name': 'Hiking', 'icon': '🥾', 'category': 'Outdoors'},
    {'name': 'Travel & Exploring', 'icon': '✈️', 'category': 'Outdoors'},
    {'name': 'Fitness & Gym', 'icon': '💪', 'category': 'Health'},
    {'name': 'Yoga & Meditation', 'icon': '🧘', 'category': 'Health'},
    {'name': 'Camping', 'icon': '⛺', 'category': 'Outdoors'},
    
    # Arts & Culture
    {'name': 'Live Music & Concerts', 'icon': '🎸', 'category': 'Music'},
    {'name': 'Art Galleries & Museums', 'icon': '🎨', 'category': 'Arts'},
    {'name': 'Photography', 'icon': '📸', 'category': 'Arts'},
    {'name': 'Reading & Literature', 'icon': '📚', 'category': 'Culture'},
    {'name': 'Cinema & Movies', 'icon': '🎬', 'category': 'Entertainment'},

    # Food & Nightlife
    {'name': 'Cooking & Baking', 'icon': '🍳', 'category': 'Food'},
    {'name': 'Coffee & Cafe Hopping', 'icon': '☕', 'category': 'Food'},
    {'name': 'Wine & Cocktails', 'icon': '🍷', 'category': 'Food'},
    {'name': 'Street Food & Foodies', 'icon': '🍜', 'category': 'Food'},

    # Tech & Gaming
    {'name': 'Video Games', 'icon': '🎮', 'category': 'Tech'},
    {'name': 'Board Games & Trivia', 'icon': '🎲', 'category': 'Entertainment'},
    {'name': 'Tech & Coding', 'icon': '💻', 'category': 'Tech'},
    {'name': 'Astrology & Horoscopes', 'icon': '✨', 'category': 'Fun'},

    # Animals & Nature
    {'name': 'Dog Lover', 'icon': '🐕', 'category': 'Animals'},
    {'name': 'Cat Lover', 'icon': '🐈', 'category': 'Animals'},
]

class Command(BaseCommand):
    help = 'Seeds initial interest tags and quiz questions for LoveMatch'

    def handle(self, *args, **options):
        # 1. Seed Interest Tags
        created_count = 0
        for item in DEFAULT_INTERESTS:
            _, created = InterestTag.objects.get_or_create(
                name=item['name'],
                defaults={'icon': item['icon'], 'category': item['category']}
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} new interest tags (Total: {InterestTag.objects.count()}).'))
