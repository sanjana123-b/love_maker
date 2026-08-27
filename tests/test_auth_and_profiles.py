import pytest
from datetime import date
from django.contrib.auth.models import User
from accounts.models import Profile, ProfilePhoto, ProfilePrompt, InterestTag


@pytest.mark.django_db
class TestAuthAndProfiles:
    def test_user_creation_triggers_profile_signal(self):
        user = User.objects.create_user(username='juliet', email='juliet@example.com', password='password123')
        assert hasattr(user, 'profile')
        assert user.profile.user == user
        assert user.profile.looking_for == 'everyone'

    def test_profile_age_calculation(self):
        user = User.objects.create_user(username='romeo', password='password123')
        today = date.today()
        user.profile.birth_date = date(today.year - 24, today.month, today.day)
        user.profile.save()
        assert user.profile.age == 24

    def test_profile_strength_meter(self):
        user = User.objects.create_user(username='sophia', password='password123')
        initial_score = user.profile.profile_strength
        assert initial_score == 0

        user.profile.bio = "Passionate coffee lover, hiker, and musician living in SF."
        user.profile.birth_date = date(1998, 5, 20)
        user.profile.city = "San Francisco"
        user.profile.interests = "hiking, music, coffee"
        user.profile.occupation = "UX Designer"
        user.profile.save()

        enhanced_score = user.profile.profile_strength
        assert enhanced_score >= 60

    def test_profile_prompt_answers(self):
        user = User.objects.create_user(username='lucas', password='password123')
        prompt = ProfilePrompt.objects.create(
            profile=user.profile,
            question="My ideal first date is...",
            answer="Getting boba and strolling through an art museum."
        )
        assert prompt.id is not None
        assert user.profile.prompts.count() == 1
        assert user.profile.prompts.first().answer == "Getting boba and strolling through an art museum."

    def test_interest_tags_association(self):
        tag1 = InterestTag.objects.create(name='Hiking', icon='🥾', category='Outdoors')
        tag2 = InterestTag.objects.create(name='Photography', icon='📸', category='Arts')
        
        user = User.objects.create_user(username='emma', password='password123')
        user.profile.interests_tags.add(tag1, tag2)
        
        assert user.profile.interests_tags.count() == 2
        assert 'Hiking' in user.profile.interests_list
        assert 'Photography' in user.profile.interests_list
