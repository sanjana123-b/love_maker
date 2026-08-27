from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class QuizQuestion(models.Model):
    CATEGORY_CHOICES = [
        ('lifestyle', 'Lifestyle'),
        ('values', 'Values'),
        ('romance', 'Romance'),
        ('interests', 'Interests'),
        ('personality', 'Personality'),
    ]
    text = models.CharField(max_length=300)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='lifestyle')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"[{self.category}] {self.text[:50]}"


class QuizAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    selected_option = models.CharField(
        max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'question']
        indexes = [
            models.Index(fields=['user', 'question']),
        ]

    def __str__(self):
        return f'{self.user.username} - Q{self.question.id}: {self.selected_option}'


class SwipeAction(models.Model):
    ACTION_CHOICES = [
        ('like', 'Like'),
        ('pass', 'Pass'),
        ('superlike', 'Super Like'),
    ]
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swipes_given')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swipes_received')
    action = models.CharField(max_length=15, choices=ACTION_CHOICES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_user', 'to_user']
        indexes = [
            models.Index(fields=['from_user', 'action']),
            models.Index(fields=['to_user', 'action']),
        ]

    def __str__(self):
        return f"{self.from_user.username} {self.action}d {self.to_user.username}"


class Like(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_given')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_received')
    is_superlike = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_user', 'to_user']
        indexes = [
            models.Index(fields=['from_user', 'to_user']),
        ]

    def __str__(self):
        star = " ⭐" if self.is_superlike else ""
        return f'{self.from_user.username} likes {self.to_user.username}{star}'


class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user2')
    is_active = models.BooleanField(default=True)
    unmatched_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='unmatched_records')
    unmatched_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user1', 'user2']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user1', 'is_active']),
            models.Index(fields=['user2', 'is_active']),
        ]

    def __str__(self):
        status = "" if self.is_active else " [Unmatched]"
        return f'{self.user1.username} ❤ {self.user2.username}{status}'

    def get_other_user(self, user):
        return self.user2 if self.user1 == user else self.user1

    def unmatch(self, user):
        """Cleanly mark match as inactive and record unmatching user."""
        self.is_active = False
        self.unmatched_by = user
        self.unmatched_at = timezone.now()
        self.save()


class DateProposal(models.Model):
    """In-Chat Date Planner & Activity proposal."""
    STATUS_CHOICES = [
        ('pending', 'Pending Response'),
        ('accepted', 'Accepted 💖'),
        ('declined', 'Declined'),
    ]
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='date_proposals')
    proposed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='date_proposals_made')
    title = models.CharField(max_length=150, help_text="e.g. Sunset Boba Walk, Arcade Night, Jazz Bar")
    details = models.TextField(max_length=500, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    suggested_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.proposed_by.username} suggested '{self.title}' ({self.status})"
