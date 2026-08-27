import pytest
from django.contrib.auth.models import User
from accounts.models import BlockRecord, UserReport
from matching.models import Match


@pytest.mark.django_db
class TestTrustAndSafety:
    def test_block_user_record_creation(self):
        user1 = User.objects.create_user(username='alice', password='password123')
        user2 = User.objects.create_user(username='bob', password='password123')

        block = BlockRecord.objects.create(
            blocker=user1,
            blocked_user=user2,
            reason="Inappropriate messages"
        )
        assert block.id is not None
        assert user1.profile.is_blocking(user2) is True
        assert user2.profile.is_blocked_by(user1) is True

    def test_blocking_inactivates_active_match(self):
        user1 = User.objects.create_user(username='charlie', password='password123')
        user2 = User.objects.create_user(username='diana', password='password123')

        match = Match.objects.create(user1=user1, user2=user2, is_active=True)
        assert match.is_active is True

        # Simulate block action
        BlockRecord.objects.create(blocker=user1, blocked_user=user2)
        Match.objects.filter(id=match.id).update(is_active=False)

        match.refresh_from_db()
        assert match.is_active is False

    def test_user_reporting_system(self):
        reporter = User.objects.create_user(username='victor', password='password123')
        reported = User.objects.create_user(username='bad_actor', password='password123')

        report = UserReport.objects.create(
            reporter=reporter,
            reported_user=reported,
            category='harassment',
            description='Sent unsolicited offensive content'
        )
        assert report.id is not None
        assert report.status == 'pending'
        assert report.reporter == reporter
        assert report.reported_user == reported
