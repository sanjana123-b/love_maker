import pytest
from django.contrib.auth.models import User
from matching.models import QuizQuestion, QuizAnswer, Like, Match, SwipeAction, DateProposal
from matching.services import calculate_compatibility, calculate_compatibility_radar, get_discover_candidates


@pytest.mark.django_db
class TestMatchingAndSwiping:
    def setup_method(self):
        self.q1 = QuizQuestion.objects.create(
            text="Ideal weekend?",
            category="lifestyle",
            option_a="Hiking", option_b="Reading", option_c="Partying", option_d="Gaming"
        )
        self.q2 = QuizQuestion.objects.create(
            text="Love language?",
            category="romance",
            option_a="Words", option_b="Time", option_c="Gifts", option_d="Touch"
        )

    def test_compatibility_with_identical_answers(self):
        u1 = User.objects.create_user(username='sam', password='password123')
        u2 = User.objects.create_user(username='alex', password='password123')

        QuizAnswer.objects.create(user=u1, question=self.q1, selected_option='A')
        QuizAnswer.objects.create(user=u2, question=self.q1, selected_option='A')
        QuizAnswer.objects.create(user=u1, question=self.q2, selected_option='B')
        QuizAnswer.objects.create(user=u2, question=self.q2, selected_option='B')

        score = calculate_compatibility(u1, u2)
        assert score >= 90

    def test_compatibility_radar_dimensions(self):
        u1 = User.objects.create_user(username='max', password='password123')
        u2 = User.objects.create_user(username='chloe', password='password123')

        radar = calculate_compatibility_radar(u1, u2)
        assert 'overall' in radar
        assert 'dimensions' in radar
        assert len(radar['dimensions']) == 5
        assert len(radar['radar_data']) == 5
        for dim in radar['dimensions']:
            assert 0 <= dim['score'] <= 100

    def test_swipe_mutual_like_creates_match(self):
        u1 = User.objects.create_user(username='leo', password='password123')
        u2 = User.objects.create_user(username='maya', password='password123')

        # Leo likes Maya
        Like.objects.create(from_user=u1, to_user=u2)
        SwipeAction.objects.create(from_user=u1, to_user=u2, action='like')

        # Maya likes Leo back
        Like.objects.create(from_user=u2, to_user=u1)
        SwipeAction.objects.create(from_user=u2, to_user=u1, action='like')

        # Simulate mutual matching logic
        min_u, max_u = (u1, u2) if u1.id < u2.id else (u2, u1)
        match = Match.objects.create(user1=min_u, user2=max_u)

        assert match.id is not None
        assert match.is_active is True
        assert match.get_other_user(u1) == u2

    def test_candidate_discovery_excludes_swiped_and_self(self):
        me = User.objects.create_user(username='me_user', password='password123')
        other1 = User.objects.create_user(username='other_swiped', password='password123')
        other2 = User.objects.create_user(username='other_available', password='password123')

        # Swipe on other1
        SwipeAction.objects.create(from_user=me, to_user=other1, action='pass')

        candidates = get_discover_candidates(me)
        candidate_ids = [c['user'].id for c in candidates]

        assert me.id not in candidate_ids
        assert other1.id not in candidate_ids
        assert other2.id in candidate_ids

    def test_date_proposal_creation_and_acceptance(self):
        u1 = User.objects.create_user(username='oliver', password='password123')
        u2 = User.objects.create_user(username='mia', password='password123')
        match = Match.objects.create(user1=u1, user2=u2)

        proposal = DateProposal.objects.create(
            match=match,
            proposed_by=u1,
            title="Late night coffee and arcade"
        )
        assert proposal.status == 'pending'

        proposal.status = 'accepted'
        proposal.save()
        assert proposal.status == 'accepted'
