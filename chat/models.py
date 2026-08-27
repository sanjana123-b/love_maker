from django.db import models
from django.contrib.auth.models import User
from matching.models import Match


class Message(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['match', 'timestamp']),
            models.Index(fields=['sender', 'is_read']),
        ]

    def __str__(self):
        return f'{self.sender.username}: {self.content[:30]}'


class MessageReaction(models.Model):
    """Message emoji reaction (e.g. ❤️, 😂, 🔥, ✨, 👍)."""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_reactions')
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user', 'emoji']

    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} on #{self.message_id}"
