import pytest
from django.contrib.auth.models import User
from matching.models import Match
from chat.models import Message, MessageReaction
from chat.ai_service import generate_spark_icebreakers


@pytest.mark.django_db
class TestChatAndAI:
    def test_message_creation_and_ordering(self):
        u1 = User.objects.create_user(username='jack', password='password123')
        u2 = User.objects.create_user(username='rose', password='password123')
        match = Match.objects.create(user1=u1, user2=u2)

        msg1 = Message.objects.create(match=match, sender=u1, content="Hello Rose!")
        msg2 = Message.objects.create(match=match, sender=u2, content="Hi Jack! So glad we matched.")

        assert match.messages.count() == 2
        assert list(match.messages.all()) == [msg1, msg2]
        assert msg1.is_read is False

    def test_message_reaction(self):
        u1 = User.objects.create_user(username='ethan', password='password123')
        u2 = User.objects.create_user(username='ava', password='password123')
        match = Match.objects.create(user1=u1, user2=u2)

        msg = Message.objects.create(match=match, sender=u1, content="You have great taste in music!")
        reaction = MessageReaction.objects.create(message=msg, user=u2, emoji="❤️")

        assert reaction.id is not None
        assert msg.reactions.count() == 1
        assert msg.reactions.first().emoji == "❤️"

    def test_ai_spark_icebreakers_generation_fallback(self):
        u1 = User.objects.create_user(username='noah', password='password123')
        u2 = User.objects.create_user(username='isabella', password='password123')
        
        u1.profile.interests = "hiking, travel, cooking"
        u2.profile.interests = "travel, photography, coffee"
        u1.profile.save()
        u2.profile.save()

        match = Match.objects.create(user1=u1, user2=u2)

        icebreakers = generate_spark_icebreakers(match, u1)
        assert isinstance(icebreakers, list)
        assert len(icebreakers) == 3
        for q in icebreakers:
            assert len(q) > 10
            assert isinstance(q, str)

    def test_unmatch_action(self):
        u1 = User.objects.create_user(username='liam', password='password123')
        u2 = User.objects.create_user(username='zoe', password='password123')
        match = Match.objects.create(user1=u1, user2=u2, is_active=True)

        match.unmatch(u1)
        assert match.is_active is False
        assert match.unmatched_by == u1
        assert match.unmatched_at is not None
