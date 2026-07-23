from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date


class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    LOOKING_FOR_CHOICES = [
        ('male', 'Men'),
        ('female', 'Women'),
        ('everyone', 'Everyone'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, default='')
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='other')
    city = models.CharField(max_length=100, blank=True, default='')
    interests = models.CharField(
        max_length=500, blank=True, default='',
        help_text='Comma-separated interests, e.g. hiking, cooking, music',
    )
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, default='')
    looking_for = models.CharField(max_length=10, choices=LOOKING_FOR_CHOICES, default='everyone')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def interests_list(self):
        if self.interests:
            return [i.strip() for i in self.interests.split(',') if i.strip()]
        return []


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
