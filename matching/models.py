from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self):
        return self.text[:50]


class QuizAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_answers')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='answers')
    selected_option = models.CharField(
        max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )

    class Meta:
        unique_together = ['user', 'question']

    def __str__(self):
        return f'{self.user.username} - Q{self.question.id}: {self.selected_option}'


class Like(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_given')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f'{self.from_user.username} likes {self.to_user.username}'


class Match(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user1', 'user2']

    def __str__(self):
        return f'{self.user1.username} \u2764 {self.user2.username}'

    def get_other_user(self, user):
        return self.user2 if self.user1 == user else self.user1
